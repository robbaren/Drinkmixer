# main.py
import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from controller import DrinkMixerController
from ui_main_qt import MainWindow

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()]
)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    logging.debug("Starting application in kiosk mode")
    try:
        controller = DrinkMixerController()
        logging.debug("Controller initialized")
        window = MainWindow(controller)
        logging.debug("MainWindow created")
        window.setGeometry(0, 0, 800, 480)
        window.showFullScreen()
        window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        window.setCursor(QCursor(Qt.CursorShape.BlankCursor))
        logging.debug("Window configured and shown")
        logging.debug("Entering event loop")
        sys.exit(app.exec())
    except Exception as e:
        logging.error("Error during execution: %s", e)
