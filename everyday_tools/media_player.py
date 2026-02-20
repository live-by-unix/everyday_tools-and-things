import tkinter as tk
from tkinter import ttk, filedialog
import vlc
import sys
import os
import time

class Player:
    def __init__(self, root):
        self.root = root
        self.root.title("Open Universal Media Player UMP RunTime Window")
        self.root.geometry("1100x700")
        
        self.is_dark_mode = True
        self.bg_color = "#121212"
        self.fg_color = "white"
        self.root.configure(bg=self.bg_color)

        if sys.platform.startswith('darwin'):
            self.instance = vlc.Instance("--no-xlib", "--quiet")
        else:
            self.instance = vlc.Instance("--no-xlib")
            
        self.player = self.instance.media_player_new()
        
        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(expand=True, fill="both")

        self.video_frame = tk.Canvas(self.main_container, bg="black", highlightthickness=0)
        self.video_frame.pack(side="left", expand=True, fill="both")

        self.playlist_frame = tk.Frame(self.main_container, bg="#1e1e1e", width=250)
        self.playlist_frame.pack(side="right", fill="y", padx=5, pady=5)
        
        self.playlist_label = tk.Label(self.playlist_frame, text="Playlist", bg="#1e1e1e", fg="white", font=("Arial", 12, "bold"))
        self.playlist_label.pack(pady=5)
        
        self.playlist_box = tk.Listbox(self.playlist_frame, bg="#252525", fg="white", selectbackground="#ADD8E6", 
                                      borderwidth=0, highlightthickness=0, font=("Arial", 10))
        self.playlist_box.pack(expand=True, fill="both", padx=5, pady=5)
        self.playlist_box.bind("<Double-Button-1>", self.play_selected)

        self.playlist_paths = []

        self.is_seeking = False
        self.is_full_screen = False
        self.paused = False
        self.is_muted = False
        self.is_repeat = False
        
        self.seek_var = tk.DoubleVar()
        self.seeker = ttk.Scale(self.root, from_=0, to=1000, orient="horizontal", 
                                variable=self.seek_var, command=self.on_seek)
        self.seeker.pack(fill="x", padx=10)
        self.seeker.bind("<ButtonPress-1>", self.start_seek)
        self.seeker.bind("<ButtonRelease-1>", self.end_seek)

        self.time_label = tk.Label(self.root, text="00:00 / 00:00", bg=self.bg_color, fg=self.fg_color)
        self.time_label.pack(pady=2)

        self.controls = tk.Frame(self.root, bg="#ADD8E6")
        self.controls.pack(fill="x", side="bottom")

        self.btn_play = tk.Button(self.controls, text="Play Media", command=self.toggle_media)
        self.btn_play.pack(side="left", padx=5)

        self.btn_open = tk.Button(self.controls, text="Open Media", command=self.open_single_file)
        self.btn_open.pack(side="left", padx=5)

        self.btn_load = tk.Button(self.controls, text="Add to Playlist", command=self.open_files)
        self.btn_load.pack(side="left", padx=5)
        
        self.btn_mute = tk.Button(self.controls, text="Mute", command=self.toggle_mute)
        self.btn_mute.pack(side="left", padx=5)

        self.btn_repeat = tk.Button(self.controls, text="Repeat: OFF", command=self.toggle_repeat)
        self.btn_repeat.pack(side="left", padx=5)

        self.btn_theme = tk.Button(self.controls, text="Toggle Theme", command=self.toggle_theme)
        self.btn_theme.pack(side="left", padx=5)

        self.vol_var = tk.DoubleVar(value=65)
        self.vol_slider = ttk.Scale(self.controls, from_=0, to=100, orient="horizontal", 
                                    variable=self.vol_var, command=self.set_volume)
        self.vol_slider.pack(side="right", padx=10)

        self.root.bind("<space>", lambda e: self.toggle_media())
        self.root.bind("<Up>", self.vol_up)
        self.root.bind("<Down>", self.vol_down)
        self.root.bind("<Left>", self.seek_backward)
        self.root.bind("<Right>", self.seek_forward)
        self.root.bind("<Escape>", self.exit_full_screen)
        self.root.bind("<m>", lambda e: self.toggle_mute())
        self.root.bind("<r>", lambda e: self.toggle_repeat())
        self.video_frame.bind("<Double-Button-1>", self.toggle_full_screen)
        
        self.update_ui_loop()

    def toggle_theme(self):
        if self.is_dark_mode:
            self.bg_color = "white"
            self.fg_color = "black"
            self.is_dark_mode = False
        else:
            self.bg_color = "#121212"
            self.fg_color = "white"
            self.is_dark_mode = True
        
        self.root.configure(bg=self.bg_color)
        self.main_container.configure(bg=self.bg_color)
        self.time_label.configure(bg=self.bg_color, fg=self.fg_color)

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.player.audio_set_mute(self.is_muted)
        self.btn_mute.config(text="Unmute" if self.is_muted else "Mute")

    def toggle_repeat(self):
        self.is_repeat = not self.is_repeat
        self.btn_repeat.config(text="Repeat: ON" if self.is_repeat else "Repeat: OFF")

    def format_time(self, ms):
        seconds = int(ms / 1000) % 60
        minutes = int(ms / 60000) % 60
        hours = int(ms / 3600000)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def open_single_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.clear_playlist()
            self.playlist_paths.append(file)
            self.playlist_box.insert(tk.END, os.path.basename(file))
            self.playlist_box.selection_set(0)
            self.play_selected()

    def open_files(self):
        files = filedialog.askopenfilenames()
        if files:
            for file in files:
                if file not in self.playlist_paths:
                    self.playlist_paths.append(file)
                    self.playlist_box.insert(tk.END, os.path.basename(file))
            if not self.player.get_media() and self.playlist_paths:
                self.playlist_box.selection_set(0)
                self.play_selected()

    def play_selected(self, event=None):
        selection = self.playlist_box.curselection()
        if selection:
            index = selection[0]
            file = self.playlist_paths[index]
            
            media = self.instance.media_new(file)
            self.player.set_media(media)

            self.root.update_idletasks()
            self.root.update()
            win_id = self.video_frame.winfo_id()

            if sys.platform.startswith('linux'):
                self.player.set_xwindow(win_id)
            elif sys.platform.startswith('win'):
                self.player.set_hwnd(win_id)
            elif sys.platform.startswith('darwin'):
                self.player.set_nsobject(win_id)

            self.player.play()
            self.paused = False
            self.btn_play.config(text="Pause Media")

    def clear_playlist(self):
        self.player.stop()
        self.playlist_paths = []
        self.playlist_box.delete(0, tk.END)
        self.time_label.config(text="00:00 / 00:00")
        self.seek_var.set(0)

    def set_volume(self, val):
        self.player.audio_set_volume(int(float(val)))

    def vol_up(self, event):
        new_vol = min(self.vol_var.get() + 5, 100)
        self.vol_var.set(new_vol)
        self.set_volume(new_vol)

    def vol_down(self, event):
        new_vol = max(self.vol_var.get() - 5, 0)
        self.vol_var.set(new_vol)
        self.set_volume(new_vol)

    def seek_forward(self, event):
        if self.player.get_media():
            curr = self.player.get_time()
            self.player.set_time(curr + 5000)

    def seek_backward(self, event):
        if self.player.get_media():
            curr = self.player.get_time()
            self.player.set_time(max(curr - 5000, 0))

    def toggle_full_screen(self, event=None):
        self.is_full_screen = not self.is_full_screen
        self.root.attributes("-fullscreen", self.is_full_screen)

    def exit_full_screen(self, event=None):
        self.is_full_screen = False
        self.root.attributes("-fullscreen", False)

    def start_seek(self, event):
        self.is_seeking = True

    def end_seek(self, event):
        if self.player.get_media():
            pos = self.seek_var.get() / 1000.0
            self.player.set_position(pos)
        self.is_seeking = False

    def on_seek(self, val):
        if self.is_seeking and self.player.get_media():
            try:
                pos = float(val) / 1000.0
                self.player.set_position(pos)
            except:
                pass

    def toggle_media(self):
        if self.player.get_media():
            if self.paused:
                self.player.play()
                self.btn_play.config(text="Pause Media")
                self.paused = False
            else:
                self.player.pause()
                self.btn_play.config(text="Play Media")
                self.paused = True
        elif self.playlist_paths:
            self.playlist_box.selection_set(0)
            self.play_selected()

    def update_ui_loop(self):
        try:
            if self.player.get_media():
                curr = self.player.get_time()
                dur = self.player.get_length()
                if curr != -1 and dur > 0:
                    self.time_label.config(text=f"{self.format_time(curr)} / {self.format_time(dur)}")
                    if not self.is_seeking and not self.paused:
                        self.seek_var.set((curr / dur) * 1000)
                
                state = self.player.get_state()
                if state == vlc.State.Ended:
                    if self.is_repeat:
                        self.player.stop()
                        self.player.play()
                    else:
                        selection = self.playlist_box.curselection()
                        if selection:
                            next_idx = selection[0] + 1
                            if next_idx < len(self.playlist_paths):
                                self.playlist_box.selection_clear(0, tk.END)
                                self.playlist_box.selection_set(next_idx)
                                self.play_selected()
        except:
            pass
        self.root.after(200, self.update_ui_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = Player(root)
    root.mainloop()