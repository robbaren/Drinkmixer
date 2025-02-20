# ui_main_qt.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QStackedWidget, QProgressBar, QScrollArea, QMessageBox,
                             QCheckBox, QLineEdit, QGridLayout, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QFont, QColor
from density_info import DENSITY_INFO
import logging

class MainWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                            stop:0 #1E1E2F, stop:1 #2A2A42);
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #00D4FF;
                color: #FFFFFF;
                border-radius: 20px;
                padding: 15px;
                font-size: 20px;
                font-family: 'Arial';
                font-weight: bold;
                border: none;
                min-width: 150px;
                min-height: 80px;
            }
            QPushButton:hover {
                background-color: #FF4081;
            }
            QPushButton:disabled {
                background-color: #6B7280;
            }
            QProgressBar {
                border: 2px solid #00D4FF;
                border-radius: 10px;
                background-color: #2A2A42;
                color: #FFFFFF;
                text-align: center;
                font-size: 18px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                  stop:0 #00D4FF, stop:1 #FF4081);
                border-radius: 8px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Arial';
            }
            QCheckBox {
                font-size: 18px;
                color: #FFFFFF;
            }
            QLineEdit {
                background-color: #3F3F5A;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
                min-height: 40px;
            }
            QTextEdit {
                background-color: #3F3F5A;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
            }
            QComboBox {
                background-color: #3F3F5A;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 10px;
                font-size: 18px;
                min-height: 40px;
            }
        """)
        self.init_ui()
        logging.debug("MainWindow initialized")

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        self.main_screen = MainScreen(self.controller, self.switch_screen)
        self.settings_screen = SettingsScreen(self.controller, self.switch_screen)
        self.hose_status_screen = HoseStatusScreen(self.controller, self.switch_screen)
        self.bottle_volumes_screen = BottleVolumesScreen(self.controller, self.switch_screen)
        self.clean_pumps_screen = CleanPumpsScreen(self.controller, self.switch_screen)
        self.recipe_editor_screen = RecipeEditorScreen(self.controller, self.switch_screen)
        self.hose_assignment_screen = HoseAssignmentScreen(self.controller, self.switch_screen)
        self.calibration_screen = CalibrationScreen(self.controller, self.switch_screen)

        self.stack.addWidget(self.main_screen)          # 0: Main
        self.stack.addWidget(self.settings_screen)      # 1: Settings
        self.stack.addWidget(self.hose_status_screen)   # 2: Hose Status
        self.stack.addWidget(self.bottle_volumes_screen)  # 3: Bottle Volumes
        self.stack.addWidget(self.clean_pumps_screen)   # 4: Clean Pumps
        self.stack.addWidget(self.recipe_editor_screen)  # 5: Recipe Editor
        self.stack.addWidget(self.hose_assignment_screen)  # 6: Hose Assignment
        self.stack.addWidget(self.calibration_screen)   # 7: Calibration
        self.stack.setCurrentIndex(0)
        logging.debug("StackedWidget populated")

    def switch_screen(self, screen_index):
        logging.debug("Switching to screen index: %s", screen_index)
        try:
            anim = QPropertyAnimation(self.stack, b"geometry")
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            current_rect = self.stack.geometry()
            anim.setStartValue(QRect(-800, current_rect.y(), 800, 480))
            anim.setEndValue(QRect(0, current_rect.y(), 800, 480))
            anim.start()
            self.stack.setCurrentIndex(screen_index)
        except Exception as e:
            logging.error("Error in switch_screen: %s", e)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Alt, Qt.Key.Key_F4):
            return
        super().keyPressEvent(event)

class MainScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Drink Mixer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #00D4FF;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.drinks_layout = QVBoxLayout(scroll_content)
        self.drinks_layout.setSpacing(10)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.refresh_drink_list()

        nav_layout = QHBoxLayout()
        settings_btn = QPushButton("\u2699 Settings")  # Gear icon
        settings_btn.clicked.connect(lambda: self.switch_callback(1))
        nav_layout.addStretch()
        nav_layout.addWidget(settings_btn)
        layout.addLayout(nav_layout)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(40)
        layout.addWidget(self.progress)

        self.is_dispensing = False
        self.mixer_worker = None

    def refresh_drink_list(self):
        logging.debug("Refreshing drink list")
        try:
            for i in reversed(range(self.drinks_layout.count())):
                self.drinks_layout.itemAt(i).widget().deleteLater()
            drinks = self.controller.get_available_drinks()
            low_volumes = self.controller.get_low_volume_hoses()
            hose_assignments = self.controller.get_hose_assignments()
            for drink in drinks:
                btn_text = drink['drink_name']
                if any(hose_id in low_volumes for hose_id, bev in hose_assignments.items() if bev.lower() in [ing.lower() for ing in drink['ingredients']]):
                    btn_text += " \u26A0"  # Warning sign
                btn = QPushButton(btn_text)
                btn.setFixedSize(300, 80)
                btn.clicked.connect(lambda checked, d=drink['drink_id']: self.on_drink_selected(d))
                self.drinks_layout.addWidget(btn)
        except Exception as e:
            logging.error("Error in refresh_drink_list: %s", e)

    def on_drink_selected(self, drink_id):
        logging.debug("Drink selected: %s", drink_id)
        try:
            if self.is_dispensing:
                QMessageBox.information(self, "Info", "A drink is already being dispensed")
                return
            dialog = QDialog(self)
            dialog.setWindowTitle("Choose Size")
            dialog.setStyleSheet("background: #2A2A42; color: #FFFFFF;")
            layout = QVBoxLayout(dialog)
            layout.setSpacing(10)
            title = QLabel("Select Size")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00D4FF;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            for size, label in [(40, "Shot (40 ml)"), (375, "Average (375 ml)"), (500, "Huge (500 ml)")]:
                btn = QPushButton(label)
                btn.setFixedSize(200, 60)
                btn.clicked.connect(lambda checked, s=size: [self.start_dispensing(drink_id, s), dialog.accept()])
                layout.addWidget(btn)
            layout.addStretch()
            dialog.exec()
        except Exception as e:
            logging.error("Error in on_drink_selected: %s", e)

    def start_dispensing(self, drink_id, size):
        logging.debug("Starting dispensing for drink_id=%s, size=%s", drink_id, size)
        try:
            self.is_dispensing = True
            self.progress.setValue(0)
            self.mixer_worker = self.controller.mix_drink(
                drink_id, size,
                self.update_progress,
                self.on_dispense_finished
            )
        except Exception as e:
            logging.error("Error in start_dispensing: %s", e)
            self.is_dispensing = False

    def update_progress(self, fraction):
        logging.debug("Updating progress: %s", fraction)
        try:
            self.progress.setValue(int(fraction * 100))
        except Exception as e:
            logging.error("Error in update_progress: %s", e)

    def on_dispense_finished(self, success):
        logging.debug("Dispensing finished with success=%s", success)
        try:
            self.is_dispensing = False
            self.refresh_drink_list()
            if success:
                QMessageBox.information(self, "Done", "Drink is ready!", QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.critical(self, "Error", "Error dispensing the drink", QMessageBox.StandardButton.Ok)
            self.mixer_worker = None
        except Exception as e:
            logging.error("Error in on_dispense_finished: %s", e)

class SettingsScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF4081;")
        layout.addWidget(title)

        status_btn = QPushButton("Hose Status")
        status_btn.clicked.connect(lambda: self.switch_callback(2))
        layout.addWidget(status_btn)

        volumes_btn = QPushButton("Bottle Volumes")
        volumes_btn.clicked.connect(lambda: self.switch_callback(3))
        layout.addWidget(volumes_btn)

        clean_btn = QPushButton("Clean Pumps")
        clean_btn.clicked.connect(lambda: self.switch_callback(4))
        layout.addWidget(clean_btn)

        recipe_btn = QPushButton("Recipe Editor")
        recipe_btn.clicked.connect(lambda: self.switch_callback(5))
        layout.addWidget(recipe_btn)

        assignment_btn = QPushButton("Hose Assignment")
        assignment_btn.clicked.connect(lambda: self.switch_callback(6))
        layout.addWidget(assignment_btn)

        calibration_btn = QPushButton("Pump Calibration")
        calibration_btn.clicked.connect(lambda: self.switch_callback(7))
        layout.addWidget(calibration_btn)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(0))
        layout.addWidget(back_btn)

class HoseStatusScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Hose Status")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #00D4FF;")
        layout.addWidget(title)

        self.checkboxes = {}
        statuses = self.controller.get_hose_status()
        for hose_id in range(1, 9):
            cb = QCheckBox(f"Hose {hose_id} Empty")
            cb.setChecked(statuses.get(hose_id, True))
            self.checkboxes[hose_id] = cb
            layout.addWidget(cb)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_hose_status)
        layout.addWidget(save_btn)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(1))
        layout.addWidget(back_btn)

    def save_hose_status(self):
        try:
            statuses = {k: cb.isChecked() for k, cb in self.checkboxes.items()}
            self.controller.update_hose_statuses(statuses)
            QMessageBox.information(self, "Success", "Hose statuses saved!")
        except Exception as e:
            logging.error("Error in save_hose_status: %s", e)
            QMessageBox.critical(self, "Error", "Failed to save hose statuses.")

class BottleVolumesScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Bottle Volumes")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF4081;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.entries = {}
        volumes = self.controller.get_bottle_volumes()
        for i, hose_id in enumerate(range(1, 9)):
            grid.addWidget(QLabel(f"Hose {hose_id}"), i, 0)
            total = QLineEdit(str(volumes.get(hose_id, {}).get('total_volume_ml', 1000)))
            remaining = QLineEdit(str(volumes.get(hose_id, {}).get('remaining_volume_ml', 1000)))
            grid.addWidget(total, i, 1)
            grid.addWidget(remaining, i, 2)
            self.entries[hose_id] = (total, remaining)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_bottle_volumes)
        layout.addWidget(save_btn)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(1))
        layout.addWidget(back_btn)

    def save_bottle_volumes(self):
        try:
            new_volumes = {}
            for k, (t, r) in self.entries.items():
                total_val = int(t.text())
                remaining_val = int(r.text())
                if total_val < 0 or remaining_val < 0 or remaining_val > total_val:
                    raise ValueError(f"Invalid values for Hose {k}")
                new_volumes[k] = {'total_volume_ml': total_val, 'remaining_volume_ml': remaining_val}
            self.controller.update_bottle_volumes(new_volumes)
            QMessageBox.information(self, "Success", "Bottle volumes saved!")
        except Exception as e:
            logging.error("Error in save_bottle_volumes: %s", e)
            QMessageBox.critical(self, "Error", str(e))

class CleanPumpsScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Clean Pumps")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #00D4FF;")
        layout.addWidget(title)

        self.status_label = QLabel("Ready to clean")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(40)
        layout.addWidget(self.progress)

        clean_btn = QPushButton("Start Cleaning")
        clean_btn.clicked.connect(self.start_cleaning)
        layout.addWidget(clean_btn)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(1))
        layout.addWidget(back_btn)

    def start_cleaning(self):
        if QMessageBox.question(self, "Clean Pumps", "Place a bowl of soapy water at the pump intakes. Proceed?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        self.status_label.setText("Starting cleaning sequence...")
        self.progress.setValue(0)
        self.worker = self.controller.clean_pumps(
            self.update_progress,
            self.on_clean_finished
        )

    def update_progress(self, message, fraction):
        logging.debug("Cleaning progress: %s, %s", message, fraction)
        try:
            self.status_label.setText(message)
            self.progress.setValue(int(fraction * 100))
        except Exception as e:
            logging.error("Error in update_progress: %s", e)

    def on_clean_finished(self, success):
        logging.debug("Cleaning finished with success=%s", success)
        try:
            if success:
                if QMessageBox.question(self, "Rinse", "Cleaning complete. Run a rinse cycle with clean water?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    self.status_label.setText("Starting rinse sequence...")
                    self.progress.setValue(0)
                    self.worker = self.controller.clean_pumps(
                        self.update_progress,
                        lambda s: self.status_label.setText("Rinse complete" if s else "Rinse failed")
                    )
                else:
                    self.status_label.setText("Cleaning complete")
            else:
                self.status_label.setText("Cleaning failed")
                QMessageBox.critical(self, "Error", "Cleaning failed")
        except Exception as e:
            logging.error("Error in on_clean_finished: %s", e)

class RecipeEditorScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.beverages = sorted(list(set(self.controller.get_hose_assignments().values())))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Recipe Editor")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF4081;")
        layout.addWidget(title)

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

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.ingredients_layout = QVBoxLayout(scroll_content)
        self.ingredients_layout.setSpacing(10)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        self.ingredient_widgets = []

        add_btn = QPushButton("Add Ingredient")
        add_btn.clicked.connect(self.add_ingredient)
        layout.addWidget(add_btn)

        save_btn = QPushButton("Save Recipe")
        save_btn.clicked.connect(self.save_recipe)
        layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete Recipe")
        delete_btn.clicked.connect(self.delete_recipe)
        layout.addWidget(delete_btn)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(1))
        layout.addWidget(back_btn)

        self.refresh_recipe_list()

    def refresh_recipe_list(self):
        logging.debug("Refreshing recipe list")
        try:
            self.id_entry.setText("")
            self.name_entry.setText("")
            self.notes_text.setText("")
            for widget in self.ingredient_widgets:
                widget[0].deleteLater()
                widget[1].deleteLater()
                widget[2].deleteLater()
            self.ingredient_widgets = []
        except Exception as e:
            logging.error("Error in refresh_recipe_list: %s", e)

    def add_ingredient(self, ingredient="", amount=0):
        hbox = QHBoxLayout()
        combo = QComboBox()
        combo.addItems(self.beverages)
        combo.setCurrentText(ingredient)
        amount_entry = QLineEdit(str(amount))
        amount_entry.setPlaceholderText("Amount (ml)")
        amount_entry.setFixedWidth(100)
        remove_btn = QPushButton("Remove")
        remove_btn.setFixedSize(100, 50)
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
                raise ValueError("Drink ID must be a positive integer")
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
            self.refresh_recipe_list()
            QMessageBox.information(self, "Success", "Recipe saved!")
        except Exception as e:
            logging.error("Error in save_recipe: %s", e)
            QMessageBox.critical(self, "Error", str(e))

    def delete_recipe(self):
        try:
            drink_id = int(self.id_entry.text())
            self.controller.delete_recipe(drink_id)
            self.refresh_recipe_list()
            QMessageBox.information(self, "Success", "Recipe deleted!")
        except Exception as e:
            logging.error("Error in delete_recipe: %s", e)
            QMessageBox.critical(self, "Error", "Invalid Drink ID or error deleting")

class HoseAssignmentScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.known_liquids = sorted(list(DENSITY_INFO.keys()))
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Hose Assignment")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #00D4FF;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        grid = QGridLayout(scroll_content)
        grid.setSpacing(10)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.comboboxes = {}
        assignments = self.controller.get_hose_assignments()
        for i, hose_id in enumerate(range(1, 9)):
            grid.addWidget(QLabel(f"Hose {hose_id}:"), i, 0)
            combo = QComboBox()
            combo.addItems(self.known_liquids)
            combo.setCurrentText(assignments.get(hose_id, ""))
            grid.addWidget(combo, i, 1)
            self.comboboxes[hose_id] = combo

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_assignments)
        layout.addWidget(save_btn)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(1))
        layout.addWidget(back_btn)

    def save_assignments(self):
        try:
            assignments = {}
            for hose_id, cb in self.comboboxes.items():
                beverage = cb.currentText().strip()
                if not beverage:
                    raise ValueError(f"Hose {hose_id} has no beverage assigned")
                assignments[hose_id] = beverage
            self.controller.update_hose_assignments(assignments)
            QMessageBox.information(self, "Success", "Hose assignments saved!")
        except Exception as e:
            logging.error("Error in save_assignments: %s", e)
            QMessageBox.critical(self, "Error", str(e))

class CalibrationScreen(QWidget):
    def __init__(self, controller, switch_callback):
        super().__init__()
        self.controller = controller
        self.switch_callback = switch_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Pump Calibration")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF4081;")
        layout.addWidget(title)

        self.pump_id_entry = QLineEdit()
        self.pump_id_entry.setPlaceholderText("Pump ID (1-8)")
        layout.addWidget(self.pump_id_entry)

        prime_btn = QPushButton("Prime Pump")
        prime_btn.clicked.connect(self.on_prime)
        layout.addWidget(prime_btn)

        self.beverage_entry = QLineEdit()
        self.beverage_entry.setPlaceholderText("New Beverage Type")
        layout.addWidget(self.beverage_entry)

        confirm_btn = QPushButton("Confirm Density")
        confirm_btn.clicked.connect(self.on_confirm_density)
        layout.addWidget(confirm_btn)

        self.volume_entry = QLineEdit()
        self.volume_entry.setPlaceholderText("Volume Dispensed (ml)")
        layout.addWidget(self.volume_entry)

        start_btn = QPushButton("Start Calibration")
        start_btn.clicked.connect(self.on_start)
        layout.addWidget(start_btn)

        stop_btn = QPushButton("Stop Calibration")
        stop_btn.clicked.connect(self.on_stop)
        layout.addWidget(stop_btn)

        self.status_label = QLabel("Ready to calibrate")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.status_label)

        layout.addStretch()
        back_btn = QPushButton("\u2B05 Back")  # Left arrow
        back_btn.clicked.connect(lambda: self.switch_callback(1))
        layout.addWidget(back_btn)

        self.density_confirmed = False

    def on_prime(self):
        try:
            pump_id = int(self.pump_id_entry.text())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            self.controller.prime_pump(pump_id)
            self.status_label.setText("Pump primed. Check liquid flow.")
        except Exception as e:
            logging.error("Error in on_prime: %s", e)
            QMessageBox.critical(self, "Error", str(e) or "Invalid pump ID")

    def on_confirm_density(self):
        try:
            pump_id = int(self.pump_id_entry.text())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            new_beverage = self.beverage_entry.text().strip()
            if not new_beverage:
                raise ValueError("Please enter the new beverage type")
            if self.controller.check_density(pump_id, new_beverage):
                self.density_confirmed = True
                self.status_label.setText("Density confirmed")
                QMessageBox.information(self, "Success", "Density is as expected")
            else:
                self.density_confirmed = False
                self.status_label.setText("Density differs")
                QMessageBox.warning(self, "Warning", "Density differs significantly")
        except Exception as e:
            logging.error("Error in on_confirm_density: %s", e)
            QMessageBox.critical(self, "Error", str(e))

    def on_start(self):
        try:
            pump_id = int(self.pump_id_entry.text())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            if not self.density_confirmed and QMessageBox.question(self, "Confirm", "Density not confirmed. Proceed?",
                                                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
            self.controller.start_calibration(pump_id)
            self.status_label.setText("Calibration started...")
        except Exception as e:
            logging.error("Error in on_start: %s", e)
            QMessageBox.critical(self, "Error", str(e))

    def on_stop(self):
        try:
            pump_id = int(self.pump_id_entry.text())
            if pump_id not in range(1, 9):
                raise ValueError("Pump ID must be 1-8")
            dispensed_volume = float(self.volume_entry.text())
            if dispensed_volume < 0:
                raise ValueError("Volume must be non-negative")
            self.controller.stop_calibration(pump_id, dispensed_volume)
            self.status_label.setText("Calibration complete")
            self.density_confirmed = False
            QMessageBox.information(self, "Success", "Calibration saved!")
        except Exception as e:
            logging.error("Error in on_stop: %s", e)
            QMessageBox.critical(self, "Error", str(e)) 
