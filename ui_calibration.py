# ui_calibration.py
import tkinter as tk
from tkinter import messagebox
from calibration_manager import start_calibration, stop_calibration, prime_pump, check_density

class CalibrationScreen(tk.Frame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.on_back = on_back

        tk.Label(self, text="Pump Calibration", font=("Helvetica", 14, "bold")).pack(pady=5)

        self.pump_id_label = tk.Label(self, text="Pump ID:")
        self.pump_id_label.pack()
        self.pump_id_entry = tk.Entry(self)
        self.pump_id_entry.pack()

        self.prime_button = tk.Button(self, text="Prime Pump", command=self.on_prime)
        self.prime_button.pack(pady=5)
        tk.Label(self, text="(Press to run pump briefly until liquid is visible)").pack()

        self.density_frame = tk.Frame(self)
        self.density_frame.pack(pady=5)
        self.new_beverage_label = tk.Label(self.density_frame, text="New Beverage Type:")
        self.new_beverage_label.grid(row=0, column=0, padx=5)
        self.new_beverage_entry = tk.Entry(self.density_frame)
        self.new_beverage_entry.grid(row=0, column=1, padx=5)
        self.confirm_density_button = tk.Button(self.density_frame, text="Confirm Beverage", command=self.on_confirm_density)
        self.confirm_density_button.grid(row=0, column=2, padx=5)

        self.volume_label = tk.Label(self, text="Volume Dispensed (ml):")
        self.volume_label.pack()
        self.volume_entry = tk.Entry(self)
        self.volume_entry.pack()

        self.start_button = tk.Button(self, text="Start Calibration", command=self.on_start)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self, text="Stop Calibration", command=self.on_stop)
        self.stop_button.pack(pady=5)

        self.back_button = tk.Button(self, text="Back", command=self.on_back_command)
        self.back_button.pack(pady=5)

        self.density_confirmed = False

    def on_prime(self):
        try:
            pump_id = int(self.pump_id_entry.get())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            prime_pump(pump_id, prime_duration=1.0)
            messagebox.showinfo("Prime Pump", "Pump primed. Check that liquid is coming out.")
        except ValueError as e:
            messagebox.showerror("Error", str(e) or "Invalid pump ID")

    def on_confirm_density(self):
        try:
            pump_id = int(self.pump_id_entry.get())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            new_beverage = self.new_beverage_entry.get().strip()
            if not new_beverage:
                raise ValueError("Please enter the new beverage type")
            if check_density(pump_id, new_beverage):
                self.density_confirmed = True
                messagebox.showinfo("Density Check", "Density is as expected")
            else:
                self.density_confirmed = False
                messagebox.showwarning("Density Check", "Density differs significantly")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_start(self):
        try:
            pump_id = int(self.pump_id_entry.get())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            if not self.density_confirmed and not messagebox.askyesno("Confirm", "Density not confirmed. Proceed?"):
                return
            start_calibration(pump_id)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_stop(self):
        try:
            pump_id = int(self.pump_id_entry.get())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            dispensed_volume = float(self.volume_entry.get())
            if dispensed_volume < 0:
                raise ValueError("Volume must be non-negative")
            stop_calibration(pump_id, dispensed_volume)
            self.density_confirmed = False
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def on_back_command(self):
        if self.on_back:
            self.on_back()
