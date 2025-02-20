# ui_recipe_editor_qt.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
                             QComboBox, QHBoxLayout, QListWidget, QMessageBox)
from PyQt6.QtCore import Qt

class RecipeEditorWindow(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Recipe Editor")
        self.setGeometry(200, 200, 500, 600)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e1e2f, stop:1 #2a2a42);
                color: #ffffff;
            }
            QLabel {
                font-size: 16px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #60a5fa;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #2a2a42;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget {
                background-color: #2a2a42;
                color: #ffffff;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Recipe Editor")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        self.recipe_list = QListWidget()
        self.recipe_list.itemClicked.connect(self.on_recipe_select)
        layout.addWidget(self.recipe_list)

        self.id_entry = QLineEdit()
        self.id_entry.setPlaceholderText("Drink ID")
        layout.addWidget(self.id_entry)

        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("Drink Name")
        layout.addWidget(self.name_entry)

        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("Notes")
        self.notes_text.setMaximumHeight(80)
        layout.addWidget(self.notes_text)

        self.ingredients_layout = QVBoxLayout()
        self.ingredient_widgets = []
        layout.addLayout(self.ingredients_layout)

        add_btn = QPushButton("Add Ingredient")
        add_btn.clicked.connect(self.add_ingredient)
        layout.addWidget(add_btn)

        save_btn = QPushButton("Save Recipe")
        save_btn.clicked.connect(self.save_recipe)
        layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete Recipe")
        delete_btn.clicked.connect(self.delete_recipe)
        layout.addWidget(delete_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.accept)
        layout.addWidget(back_btn)

        self.refresh_recipe_list()

    def refresh_recipe_list(self):
        self.recipe_list.clear()
        for recipe in self.controller.get_available_drinks():
            self.recipe_list.addItem(f"{recipe['drink_id']} - {recipe['drink_name']}")

    def on_recipe_select(self, item):
        drink_id = int(item.text().split(" - ")[0])
        recipe = self.controller.get_recipe_by_id(drink_id)
        self.id_entry.setText(str(recipe['drink_id']))
        self.id_entry.setEnabled(False)
        self.name_entry.setText(recipe['drink_name'])
        self.notes_text.setText(recipe['notes'])
        for widget in self.ingredient_widgets:
            widget[0].deleteLater()
            widget[1].deleteLater()
            widget[2].deleteLater()
        self.ingredient_widgets = []
        for ing, amount in recipe['ingredients'].items():
            self.add_ingredient(ing, amount)

    def add_ingredient(self, ingredient="", amount=0):
        hbox = QHBoxLayout()
        combo = QComboBox()
        combo.addItems(sorted(self.controller.get_hose_assignments().values()))
        combo.setCurrentText(ingredient)
        amount_entry = QLineEdit(str(amount))
        amount_entry.setPlaceholderText("Amount (ml)")
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: [hbox.itemAt(0).widget().deleteLater(), 
                                            hbox.itemAt(1).widget().deleteLater(), 
                                            hbox.itemAt(2).widget().deleteLater(), 
                                            self.ingredient_widgets.remove((combo, amount_entry, remove_btn))])
        hbox.addWidget(combo)
        hbox.addWidget(amount_entry)
        hbox.addWidget(remove_btn)
        self.ingredients_layout.addLayout(hbox)
        self.ingredient_widgets.append((combo, amount_entry, remove_btn))

    def save_recipe(self):
        try:
            drink_id = int(self.id_entry.text())
            if drink_id < 1:
                raise ValueError("Drink ID must be positive")
            name = self.name_entry.text().strip()
            if not name:
                raise ValueError("Drink name is required")
            ingredients = {}
            for combo, entry, _ in self.ingredient_widgets:
                ing = combo.currentText().strip()
                if not ing:
                    continue
                amount = int(entry.text())
                if amount <= 0:
                    raise ValueError(f"Amount for {ing} must be positive")
                ingredients[ing] = amount
            if not ingredients:
                raise ValueError("At least one ingredient required")
            notes = self.notes_text.toPlainText().strip()
            self.controller.save_recipe(drink_id, name, ingredients, notes)
            self.id_entry.setEnabled(True)
            self.clear_form()
            self.refresh_recipe_list()
            QMessageBox.information(self, "Saved", "Recipe saved successfully")
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_recipe(self):
        try:
            drink_id = int(self.id_entry.text())
            self.controller.delete_recipe(drink_id)
            self.clear_form()
            self.refresh_recipe_list()
            QMessageBox.information(self, "Deleted", "Recipe deleted successfully")
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid Drink ID")

    def clear_form(self):
        self.id_entry.setEnabled(True)
        self.id_entry.clear()
        self.name_entry.clear()
        self.notes_text.clear()
        for widget in self.ingredient_widgets:
            widget[0].deleteLater()
            widget[1].deleteLater()
            widget[2].deleteLater()
        self.ingredient_widgets = []
