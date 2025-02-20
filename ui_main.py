# ui_main.py
import tkinter as tk
from tkinter import ttk, messagebox

class MainScreen(tk.Frame):
    def __init__(self, master, controller, on_settings=None):
        super().__init__(master)
        self.controller = controller
        self.on_settings = on_settings
        
        tk.Label(self, text="Smart Drinkmixer", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.status_frame = tk.Frame(self)
        self.status_frame.pack(fill=tk.X, pady=5)
        self.update_status()

        self.drinks_frame = tk.Frame(self)
        self.drinks_frame.pack(fill=tk.BOTH, expand=True)

        self.refresh_drink_list()

        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10)

        self.settings_button = tk.Button(self, text="Settings", command=self.on_settings_command)
        self.settings_button.pack(pady=5)

        self.is_dispensing = False

    def update_status(self):
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        statuses = self.controller.get_hose_status()
        volumes = self.controller.get_bottle_volumes()
        for hose_id in range(1, 9):
            is_empty = statuses.get(hose_id, True)
            remaining = volumes.get(hose_id, {}).get('remaining_volume_ml', 0)
            color = "red" if is_empty or remaining <= 0 else "green"
            tk.Label(self.status_frame, text=f"H{hose_id}", bg=color, fg="white", width=5).pack(side=tk.LEFT, padx=2)

    def refresh_drink_list(self):
        for widget in self.drinks_frame.winfo_children():
            widget.destroy()
        drinks = self.controller.get_available_drinks()
        low_volumes = self.controller.get_low_volume_hoses()
        hose_assignments = self.controller.get_hose_assignments()
        for drink in drinks:
            container = tk.Frame(self.drinks_frame, bd=1, relief=tk.RAISED, padx=5, pady=5)
            container.pack(fill=tk.X, padx=5, pady=5)
            btn_text = drink['drink_name']
            if any(hose_id in low_volumes for hose_id, bev in hose_assignments.items() if bev.lower() in [ing.lower() for ing in drink['ingredients']]):
                btn_text += " ⚠️ (Low Volume)"
            btn = tk.Button(container, text=btn_text, font=("Helvetica", 12, "bold"),
                            command=lambda d=drink: self.on_drink_selected(d['drink_id']))
            btn.pack(side=tk.TOP, fill=tk.X)
            note = drink.get('notes', "")
            if note:
                tk.Label(container, text=note, fg="grey", font=("Helvetica", 9)).pack(side=tk.TOP, fill=tk.X)
        self.update_status()

    def on_settings_command(self):
        if self.on_settings:
            self.on_settings()

    def on_drink_selected(self, drink_id):
        if self.is_dispensing:
            messagebox.showinfo("Info", "A drink is already being dispensed")
            return
        size_dialog = tk.Toplevel(self)
        size_dialog.title("Choose Drink Size")
        tk.Label(size_dialog, text="Select Drink Size:", font=("Helvetica", 12, "bold")).pack(pady=10)
        tk.Button(size_dialog, text="Shot (40 ml)", command=lambda: [size_dialog.destroy(), self.start_dispensing(drink_id, 40)]).pack(pady=5)
        tk.Button(size_dialog, text="Average (375 ml)", command=lambda: [size_dialog.destroy(), self.start_dispensing(drink_id, 375)]).pack(pady=5)
        tk.Button(size_dialog, text="Huge (500 ml)", command=lambda: [size_dialog.destroy(), self.start_dispensing(drink_id, 500)]).pack(pady=5)

    def start_dispensing(self, drink_id, chosen_size):
        self.is_dispensing = True
        self.progress['value'] = 0
        self.disable_buttons()
        self.controller.mix_drink(
            drink_id, chosen_size,
            progress_callback=lambda f: self.after(0, self.update_progress, f),
            finished_callback=lambda s: self.after(0, self.on_dispense_finished, s)
        )

    def update_progress(self, fraction):
        self.progress['value'] = fraction * 100

    def on_dispense_finished(self, success):
        self.is_dispensing = False
        self.enable_buttons()
        self.refresh_drink_list()
        if success:
            messagebox.showinfo("Done", "Drink is ready!")
        else:
            messagebox.showerror("Error", "Error dispensing the drink")

    def disable_buttons(self):
        for child in self.drinks_frame.winfo_children():
            for widget in child.winfo_children():
                widget.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        for child in self.drinks_frame.winfo_children():
            for widget in child.winfo_children():
                widget.config(state=tk.NORMAL)
        self.settings_button.config(state=tk.NORMAL)
