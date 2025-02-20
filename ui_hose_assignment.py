# ui_hose_assignment.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import config_manager
from density_info import DENSITY_INFO, add_density

class HoseAssignmentScreen(tk.Frame):
    def __init__(self, master, on_back=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_back = on_back
        self.known_liquids = sorted(list(DENSITY_INFO.keys()))
        self.hose_ids = range(1, 9)
        self.comboboxes = {}
        tk.Label(self, text="Beverage Assignment", font=("Helvetica", 16, "bold")).pack(pady=10)
        self.create_widgets()
        tk.Button(self, text="Save All", command=self.save_assignments).pack(pady=5)
        tk.Button(self, text="Back", command=self.on_back_command).pack(pady=5)

    def create_widgets(self):
        current_assignments = config_manager.load_hose_assignments()
        for hose_id in self.hose_ids:
            frame = tk.Frame(self)
            frame.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(frame, text=f"Hose {hose_id}:").pack(side=tk.LEFT, padx=5)
            current_value = current_assignments.get(hose_id, "")
            combobox = ttk.Combobox(frame, values=self.known_liquids)
            combobox.set(current_value)
            combobox.pack(side=tk.LEFT, padx=5)
            self.comboboxes[hose_id] = combobox
            tk.Button(frame, text="Add New", command=lambda hid=hose_id: self.add_new_liquid(hid)).pack(side=tk.LEFT, padx=5)

    def add_new_liquid(self, hose_id):
        new_liquid = simpledialog.askstring("Add New Beverage", "Enter new beverage name:")
        if not new_liquid or not new_liquid.strip():
            return
        try:
            density_str = simpledialog.askstring("Density", "Enter density (g/ml) for this beverage:")
            density = float(density_str)
            if density <= 0:
                raise ValueError("Density must be positive")
            new_liquid_lower = new_liquid.lower().strip()
            if new_liquid_lower not in [liq.lower() for liq in self.known_liquids]:
                self.known_liquids.append(new_liquid)
                self.known_liquids.sort()
                add_density(new_liquid, density)
                for cb in self.comboboxes.values():
                    cb['values'] = self.known_liquids
                self.comboboxes[hose_id].set(new_liquid)
            else:
                messagebox.showinfo("Info", f"{new_liquid} already exists")
        except ValueError as e:
            messagebox.showerror("Error", str(e) or "Invalid density value")

    def save_assignments(self):
        assignments = {}
        for hose_id, cb in self.comboboxes.items():
            beverage = cb.get().strip()
            if not beverage:
                messagebox.showerror("Error", f"Hose {hose_id} has no beverage assigned")
                return
            assignments[hose_id] = beverage
        config_manager.save_hose_assignments(assignments)
        messagebox.showinfo("Saved", "Hose assignments saved successfully")

    def on_back_command(self):
        if self.on_back:
            self.on_back()
