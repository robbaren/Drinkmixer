# ui_recipe_editor.py
import tkinter as tk
from tkinter import ttk, messagebox
from recipe_manager import load_all_recipes, save_recipe, delete_recipe
from config_manager import load_hose_assignments

class RecipeEditorScreen(tk.Frame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.on_back = on_back
        self.hose_assignments = load_hose_assignments()
        self.beverages = sorted(list(set(self.hose_assignments.values())))

        tk.Label(self, text="Recipe Editor", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.recipe_listbox = tk.Listbox(self, height=10)
        self.recipe_listbox.pack(fill=tk.X, padx=10, pady=5)
        self.recipe_listbox.bind('<<ListboxSelect>>', self.on_recipe_select)

        self.form_frame = tk.Frame(self)
        self.form_frame.pack(fill=tk.BOTH, padx=10, pady=5)

        tk.Label(self.form_frame, text="Drink ID:").grid(row=0, column=0, sticky="e")
        self.id_entry = tk.Entry(self.form_frame)
        self.id_entry.grid(row=0, column=1, pady=2)

        tk.Label(self.form_frame, text="Drink Name:").grid(row=1, column=0, sticky="e")
        self.name_entry = tk.Entry(self.form_frame)
        self.name_entry.grid(row=1, column=1, pady=2)

        tk.Label(self.form_frame, text="Notes:").grid(row=2, column=0, sticky="ne")
        self.notes_text = tk.Text(self.form_frame, height=3, width=30)
        self.notes_text.grid(row=2, column=1, pady=2)

        self.ingredients_frame = tk.Frame(self.form_frame)
        self.ingredients_frame.grid(row=3, column=0, columnspan=2, pady=5)
        self.ingredient_entries = []

        tk.Button(self, text="Add Ingredient", command=self.add_ingredient).pack(pady=2)
        tk.Button(self, text="Save Recipe", command=self.save_recipe).pack(pady=2)
        tk.Button(self, text="Delete Recipe", command=self.delete_recipe).pack(pady=2)
        tk.Button(self, text="Back", command=self.on_back_command).pack(pady=5)

        self.refresh_recipe_list()

    def refresh_recipe_list(self):
        self.recipe_listbox.delete(0, tk.END)
        for recipe in load_all_recipes():
            self.recipe_listbox.insert(tk.END, f"{recipe['drink_id']} - {recipe['drink_name']}")

    def on_recipe_select(self, event):
        selection = self.recipe_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        recipe = load_all_recipes()[index]
        self.id_entry.delete(0, tk.END)
        self.id_entry.insert(0, recipe['drink_id'])
        self.id_entry.config(state='disabled')
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, recipe['drink_name'])
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, recipe['notes'])
        for widget in self.ingredients_frame.winfo_children():
            widget.destroy()
        self.ingredient_entries = []
        for ing, amount in recipe['ingredients'].items():
            self.add_ingredient(ing, amount)

    def add_ingredient(self, ingredient="", amount=0):
        frame = tk.Frame(self.ingredients_frame)
        frame.pack(fill=tk.X, pady=2)
        combo = ttk.Combobox(frame, values=self.beverages)
        combo.set(ingredient)
        combo.pack(side=tk.LEFT, padx=5)
        entry = tk.Entry(frame, width=10)
        entry.insert(0, amount)
        entry.pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Remove", command=lambda: [frame.destroy(), self.ingredient_entries.remove((combo, entry))]).pack(side=tk.LEFT)
        self.ingredient_entries.append((combo, entry))

    def save_recipe(self):
        try:
            drink_id = int(self.id_entry.get())
            if drink_id < 1:
                raise ValueError("Drink ID must be a positive integer")
            drink_name = self.name_entry.get().strip()
            if not drink_name:
                raise ValueError("Drink name is required")
            ingredients = {}
            for combo, entry in self.ingredient_entries:
                ing = combo.get().strip()
                if not ing:
                    continue
                amount = int(entry.get())
                if amount <= 0:
                    raise ValueError(f"Amount for {ing} must be positive")
                ingredients[ing] = amount
            if not ingredients:
                raise ValueError("At least one ingredient is required")
            notes = self.notes_text.get(1.0, tk.END).strip()
            save_recipe(drink_id, drink_name, ingredients, notes)
            self.id_entry.config(state='normal')
            self.clear_form()
            self.refresh_recipe_list()
            messagebox.showinfo("Saved", "Recipe saved successfully")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_recipe(self):
        try:
            drink_id = int(self.id_entry.get())
            delete_recipe(drink_id)
            self.clear_form()
            self.refresh_recipe_list()
            messagebox.showinfo("Deleted", "Recipe deleted successfully")
        except ValueError:
            messagebox.showerror("Error", "Invalid Drink ID")

    def clear_form(self):
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.notes_text.delete(1.0, tk.END)
        for widget in self.ingredients_frame.winfo_children():
            widget.destroy()
        self.ingredient_entries = []

    def on_back_command(self):
        if self.on_back:
            self.on_back()
