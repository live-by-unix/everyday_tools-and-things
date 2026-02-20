import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import customtkinter as ctk
import json
import os

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MONEY Manager 💸")
        self.geometry("1100x700")
        ctk.set_appearance_mode("Dark")

        # Data initialization
        self.data_file = "finance_data.json"
        self.categories = ['Rent', 'Food', 'Subscribes', 'Fun', 'Other']
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#808000']
        self.last_saved_values = [] 

        self.load_data()

        # Layout Configuration
        self.grid_columnconfigure(1, weight=3) # Give more weight to chart area
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="Update Spending", font=("Arial", 24, "bold")).pack(pady=20)

        # Monthly Budget Input
        frame_budget = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_budget.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(frame_budget, text="Monthly Budget:", font=("Arial", 13, "bold")).pack(side="left")
        self.budget_entry = ctk.CTkEntry(frame_budget, width=100)
        self.budget_entry.insert(0, str(self.budget))
        self.budget_entry.pack(side="right")

        # Category Entries
        self.entries = {}
        for i, cat in enumerate(self.categories):
            frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(frame, text=cat, width=100, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame, width=100)
            entry.insert(0, str(self.values[i]))
            entry.pack(side="right")
            self.entries[cat] = entry

        self.total_label = ctk.CTkLabel(self.sidebar, text="", font=("Arial", 18, "bold"))
        self.total_label.pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Save Changes", command=self.manual_update, fg_color="#2c82c9").pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Reset All Data", fg_color="#A03030", hover_color="#D03030", command=self.reset_data).pack(pady=10)

        # --- Chart & Info Area ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.chart_frame = ctk.CTkFrame(self.main_container, fg_color="#2b2b2b", corner_radius=15)
        self.chart_frame.grid(row=0, column=0, sticky="nsew")
        
        self.canvas = None
        self.manual_update() # Initial draw
        self.auto_save_loop()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    saved_data = json.load(f)
                    self.values = saved_data.get("values", [0] * len(self.categories))
                    self.budget = saved_data.get("budget", 3000)
            except Exception:
                self.values, self.budget = [0] * len(self.categories), 3000
        else:
            self.values, self.budget = [0] * len(self.categories), 3000

    def save_logic(self):
        try:
            current_values = [float(self.entries[cat].get() or 0) for cat in self.categories]
            current_budget = float(self.budget_entry.get() or 0)
            
            # Check if data actually changed before saving/refreshing
            if current_values != self.values or current_budget != self.budget:
                self.values = current_values
                self.budget = current_budget
                with open(self.data_file, "w") as f:
                    json.dump({"values": self.values, "budget": self.budget}, f)
                return True 
        except ValueError:
            pass 
        return False 

    def auto_save_loop(self):
        """Refreshes UI only if data has changed."""
        if self.save_logic():
            self.create_chart()
        self.after(2000, self.auto_save_loop) 

    def manual_update(self):
        self.save_logic()
        self.create_chart()

    def reset_data(self):
        self.values = [0] * len(self.categories)
        self.budget = 3000
        self.budget_entry.delete(0, 'end')
        self.budget_entry.insert(0, "3000")
        for cat in self.categories:
            self.entries[cat].delete(0, 'end')
            self.entries[cat].insert(0, "0")
        self.manual_update()

    def create_chart(self):
        # Clear previous canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        total_spent = sum(self.values)
        remaining = self.budget - total_spent
        
        status_color = "#52D017" if remaining >= 0 else "#FF6347"
        self.total_label.configure(
            text=f"Total Spent: ${total_spent:,.2f}\nRemaining: ${remaining:,.2f}", 
            text_color=status_color
        )

        # Matplotlib Figure
        fig = plt.figure(figsize=(6, 5), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        
        display_values = []
        display_labels = []
        display_colors = []
        
        for i, val in enumerate(self.values):
            if val > 0:
                display_values.append(val)
                display_labels.append(self.categories[i])
                display_colors.append(self.colors[i])

        if display_values:
            wedges, texts, autotexts = ax.pie(
                display_values, labels=display_labels, autopct='%1.1f%%', 
                startangle=140, colors=display_colors, 
                textprops={'color':"w", 'weight': 'bold'}, pctdistance=0.85
            )
            # Draw the center circle for the donut look
            centre_circle = plt.Circle((0,0), 0.70, fc='#2b2b2b')
            fig.gca().add_artist(centre_circle)
        else:
            ax.text(0.5, 0.5, 'Enter spending to\nsee visualization', 
                    color='gray', ha='center', va='center', fontsize=14)
        
        ax.axis('off')

        # Link Matplotlib to CustomTkinter
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        plt.close(fig)

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()