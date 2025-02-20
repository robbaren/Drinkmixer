# ui_settings_qt.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit,
                             QMessageBox, QProgressBar, QCheckBox, QGridLayout)
from PyQt6.QtCore import Qt
from ui_recipe_editor_qt import RecipeEditorWindow

class SettingsWindow(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Settings")
        self.setGeometry(150, 150, 400, 600)
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
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #60a5fa;
            }
            QLineEdit, QCheckBox {
                background-color: #2a2a42;
                color: #ffffff;
                border: 1px solid #3b82f6;
                border-radius: 5px;
                padding: 5px;
            }
            QProgressBar {
                border: 2px solid #3b82f6;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
                background-color: #2a2a42;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Settings")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        self.add_button("Beverage Assignment", self.show_hose_assignment, layout)
        self.add_button("Hose Status Update", self.show_hose_status, layout)
        self.add_button("Bottle Volume Definition", self.show_bottle_volumes, layout)
        self.add_button("Pump Calibration", self.show_calibration, layout)
        self.add_button("Clean Pumps", self.show_clean_pumps, layout)
        self.add_button("Recipe Editor", self.show_recipe_editor, layout)
        self.add_button("Back", self.close, layout)

    def add_button(self, text, callback, layout):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        layout.addWidget(btn)

    def show_hose_assignment(self):
        QMessageBox.information(self, "Info", "Hose Assignment not yet implemented in Qt UI")

    def show_hose_status(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Hose Status Update")
        dialog.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dialog)
        statuses = self.controller.get_hose_status()
        checkboxes = {}
        for hose_id in range(1, 9):
            cb = QCheckBox(f"Hose {hose_id} Empty")
            cb.setChecked(statuses.get(hose_id, True))
            checkboxes[hose_id] = cb
            layout.addWidget(cb)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: [self.controller.update_hose_statuses({k: cb.isChecked() for k, cb in checkboxes.items()}), dialog.accept()])
        layout.addWidget(save_btn)
        dialog.exec()

    def show_bottle_volumes(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Bottle Volume Definition")
        dialog.setStyleSheet(self.styleSheet())
        layout = QGridLayout(dialog)
        volumes = self.controller.get_bottle_volumes()
        entries = {}
        for i, hose_id in enumerate(range(1, 9), 0):
            layout.addWidget(QLabel(f"Hose {hose_id} Total (ml):"), i, 0)
            total = QLineEdit(str(volumes.get(hose_id, {}).get('total_volume_ml', 1000)))
            layout.addWidget(total, i, 1)
            layout.addWidget(QLabel("Remaining (ml):"), i, 2)
            remaining = QLineEdit(str(volumes.get(hose_id, {}).get('remaining_volume_ml', 1000)))
            layout.addWidget(remaining, i, 3)
            entries[hose_id] = (total, remaining)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_bottle_volumes(entries, dialog))
        layout.addWidget(save_btn, 8, 0, 1, 4)
        dialog.exec()

    def save_bottle_volumes(self, entries, dialog):
        try:
            new_volumes = {}
            for k, (t, r) in entries.items():
                total_val = int(t.text())
                remaining_val = int(r.text())
                if total_val < 0 or remaining_val < 0 or remaining_val > total_val:
                    raise ValueError(f"Invalid values for Hose {k}")
                new_volumes[k] = {'total_volume_ml': total_val, 'remaining_volume_ml': remaining_val}
            self.controller.update_bottle_volumes(new_volumes)
            dialog.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_calibration(self):
        QMessageBox.information(self, "Info", "Pump Calibration not yet implemented in Qt UI")

    def show_clean_pumps(self):
        reply = QMessageBox.question(self, "Clean Pumps", "Place a bowl of soapy water at the pump intakes. Proceed?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Cleaning Pumps")
        dialog.setStyleSheet(self.styleSheet())
        layout = QVBoxLayout(dialog)
        status_label = QLabel("Starting cleaning sequence...")
        layout.addWidget(status_label)
        progress = QProgressBar()
        progress.setMaximum(100)
        layout.addWidget(progress)

        def update_progress(message, fraction):
            status_label.setText(message)
            progress.setValue(int(fraction * 100))
            dialog.update()

        def on_finished(success):
            if success:
                rinse = QMessageBox.question(self, "Rinse", "Cleaning complete. Run a rinse cycle with clean water?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if rinse == QMessageBox.StandardButton.Yes:
                    self.controller.clean_pumps(update_progress, lambda s: dialog.accept() if s else QMessageBox.critical(self, "Error", "Rinse failed"))
                else:
                    dialog.accept()
            else:
                QMessageBox.critical(self, "Error", "Cleaning failed")
                dialog.accept()

        self.controller.clean_pumps(update_progress, on_finished)
        dialog.exec()

    def show_recipe_editor(self):
        self.recipe_editor = RecipeEditorWindow(self.controller, self)
        self.recipe_editor.show()
