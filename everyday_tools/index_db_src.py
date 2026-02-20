import customtkinter as ctk
import sqlite3
import subprocess
import threading
import os
import platform
import sys

class IndexDB(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Index@DB")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.db_path = os.path.join(os.path.expanduser("~"), "index_data.db")
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.init_db()

        self.label = ctk.CTkLabel(self, text="Index@DB", font=("Arial", 24, "bold"))
        self.label.pack(pady=(20, 10))

        self.entry = ctk.CTkEntry(
            self, 
            placeholder_text="Find your file.", 
            width=700, 
            height=45,
            font=("Arial", 16)
        )
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.on_type)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=950, height=500)
        self.scrollable_frame.pack(pady=10, padx=20)

        self.status_label = ctk.CTkLabel(self, text="Initializing...", text_color="gray")
        self.status_label.pack(side="bottom", pady=10)

        threading.Thread(target=self.index_system, daemon=True).start()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS files (name TEXT, path TEXT)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON files(name)") 
        self.conn.commit()

    def index_system(self):
        self.status_label.configure(text="Indexing EVERY file... (This may take some time)", text_color="orange")
        search_root = os.path.expanduser("~") 
        
        # Optimized command for Mac to skip hidden folders and library junk
        cmd = f"find {search_root} -xdev -not -path '*/.*' -not -path '*/Library/*' 2>/dev/null"
        
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, text=True, bufsize=1)
            batch = []
            count = 0
            
            for line in process.stdout:
                full_path = line.strip()
                file_name = os.path.basename(full_path)
                batch.append((file_name, full_path))
                count += 1
                
                if len(batch) >= 5000:
                    self.save_batch(batch)
                    batch = []
                    self.status_label.configure(text=f"Total Files Indexed: {count:,}")

            self.save_batch(batch)
            self.status_label.configure(text=f"Success! {count:,} files indexed.", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"Indexer Error: {e}", text_color="red")

    def save_batch(self, batch):
        cursor = self.conn.cursor()
        cursor.executemany("INSERT INTO files VALUES (?, ?)", batch)
        self.conn.commit()

    def on_type(self, event):
        query = self.entry.get().strip()
        if len(query) >= 3:
            self.search(query)

    def search(self, query):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name, path FROM files WHERE name LIKE ? ORDER BY name ASC LIMIT 100", 
            ('%' + query + '%',)
        )
        results = cursor.fetchall()
        
        for name, path in results:
            btn = ctk.CTkButton(
                self.scrollable_frame, 
                text=f"{name[:40].ljust(45)} | {path}", 
                anchor="w", 
                fg_color="transparent", 
                hover_color="#2B2B2B",
                font=("Courier", 13),
                command=lambda p=path: self.open_file(p)
            )
            btn.pack(fill="x", pady=1)

    def open_file(self, path):
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            print(f"Could not open file: {e}")
if __name__ == "__main__":
    app = IndexDB()
    app.mainloop()