# ui_settings.py
import tkinter as tk
from tkinter import messagebox, ttk
from config_manager import load_hose_statuses, save_hose_statuses, load_bottle_volumes, save_bottle_volumes
from drink_mixer import clean_pumps

CORRECT_PIN = "1234"

class SettingsMenu(tk.Frame):
    def __init__(self, master, on_back=None, on_open_calibration=None, on_open_hose_assignment=None, on_open_recipe_editor=None):
        super().__init__(master)
        self.on_back = on_back
        self.on_open_calibration = on_open_calibration
        self.on_open_hose_assignment = on_open_hose_assignment
        self.on_open_recipe_editor = on_open_recipe_editor
        
        tk.Label(self, text="Settings Menu", font=("Helvetica", 16, "bold")).pack(pady=5)
        
        tk.Button(self, text="Beverage Assignment", command=self.on_open_hose_assignment).pack(pady=2)
        tk.Button(self, text="Hose Status Update", command=self.show_hose_status).pack(pady=2)
        tk.Button(self, text="Bottle Volume Definition", command=self.show_bottle_volumes).pack(pady=2)
        tk.Button(self, text="Pump Calibration", command=self.on_open_calibration).pack(pady=2)
        tk.Button(self, text="Clean Pumps", command=self.show_clean_pumps).pack(pady=2)
        tk.Button(self, text="Recipe Editor", command=self.on_open_recipe_editor).pack(pady=2)
        tk.Button(self, text="Back", command=self.on_back_command).pack(pady=2)

    def show_hose_status(self):
        top = tk.Toplevel(self)
        top.title("Hose Status Update")
        statuses = load_hose_statuses()
        vars = {}
        for hose_id in range(1, 9):
            var = tk.BooleanVar(value=statuses.get(hose_id, True))
            tk.Checkbutton(top, text=f"Hose {hose_id} Empty", variable=var).pack(pady=2)
            vars[hose_id] = var
        tk.Button(top, text="Save", command=lambda: [save_hose_statuses({k: v.get() for k, v in vars.items()}), top.destroy()]).pack(pady=5)

    def show_bottle_volumes(self):
        top = tk.Toplevel(self)
        top.title("Bottle Volume Definition")
        volumes = load_bottle_volumes()
        entries = {}
        for hose_id in range(1, 9):
            frame = tk.Frame(top)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=f"Hose {hose_id} Total (ml):").pack(side=tk.LEFT)
            total = tk.Entry(frame)
            total.insert(0, volumes.get(hose_id, {}).get('total_volume_ml', 1000))
            total.pack(side=tk.LEFT, padx=5)
            tk.Label(frame, text="Remaining (ml):").pack(side=tk.LEFT)
            remaining = tk.Entry(frame)
            remaining.insert(0, volumes.get(hose_id, {}).get('remaining_volume_ml', 1000))
            remaining.pack(side=tk.LEFT, padx=5)
            entries[hose_id] = (total, remaining)
        def save_volumes():
            try:
                new_volumes = {}
                for k, (t, r) in entries.items():
                    total_val = int(t.get())
                    remaining_val = int(r.get())
                    if total_val < 0 or remaining_val < 0 or remaining_val > total_val:
                        raise ValueError(f"Invalid values for Hose {k}")
                    new_volumes[k] = {'total_volume_ml': total_val, 'remaining_volume_ml': remaining_val}
                save_bottle_volumes(new_volumes)
                top.destroy()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        tk.Button(top, text="Save", command=save_volumes).pack(pady=5)

    def show_clean_pumps(self):
        if not messagebox.askyesno("Clean Pumps", "Place a bowl of soapy water at the pump intakes. Proceed?"):
            return
        top = tk.Toplevel(self)
        top.title("Cleaning Pumps")
        status_label = tk.Label(top, text="Starting cleaning sequence...", font=("Helvetica", 12))
        status_label.pack(pady=10)
        progress = ttk.Progressbar(top, orient="horizontal", length=200, mode="determinate")
        progress.pack(pady=10)

        def update_progress(message, fraction):
            status_label.config(text=message)
            progress['value'] = fraction * 100
            top.update_idletasks()

        def on_finished(success):
            if success:
                if messagebox.askyesno("Rinse", "Cleaning complete. Run a rinse cycle with clean water?"):
                    clean_pumps(progress_callback=update_progress, finished_callback=lambda s: top.destroy() if s else messagebox.showerror("Error", "Rinse failed"))
                else:
                    top.destroy()
            else:
                messagebox.showerror("Error", "Cleaning failed")
                top.destroy()

        clean_pumps(progress_callback=update_progress, finished_callback=on_finished)

    def on_back_command(self):
        if self.on_back:
            self.on_back()

class PINEntryScreen(tk.Frame):
    def __init__(self, master, on_success=None, on_cancel=None):
        super().__init__(master)
        self.on_success = on_success
        self.on_cancel = on_cancel

        tk.Label(self, text="Enter PIN:").pack()
        self.pin_entry = tk.Entry(self, show="*")
        self.pin_entry.pack()

        tk.Button(self, text="Submit", command=self.check_pin).pack(pady=5)
        tk.Button(self, text="Cancel", command=self.on_cancel_command).pack(pady=5)

    def check_pin(self):
        pin_input = self.pin_entry.get()
        if pin_input == CORRECT_PIN:
            if self.on_success:
                self.on_success()
        else:
            messagebox.showerror("Error", "Invalid PIN")

    def on_cancel_command(self):
        if self.on_cancel:
            self.on_cancel()
