# drink_mixer.py
import time
import logging
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox
from config_manager import (
    load_hose_assignments, load_pump_calibrations, update_remaining_volume,
    load_bottle_volumes, save_bottle_volumes
)
from recipe_manager import get_recipe_by_id

PUMP_GPIO_PINS = {1: 17, 2: 18, 3: 27, 4: 22, 5: 23, 6: 24, 7: 25, 8: 5}

class PumpManager(QObject):
    def __init__(self):
        super().__init__()
        self.gpio_initialized = False

    def initialize_gpio(self):
        if GPIO and not self.gpio_initialized:
            logging.debug("Initializing GPIO")
            try:
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                for pin in PUMP_GPIO_PINS.values():
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)
                self.gpio_initialized = True
            except Exception as e:
                logging.error(f"GPIO initialization failed: {e}")

    def activate_pump(self, pump_id, dispense_time):
        if not GPIO:
            logging.warning(f"GPIO not available, simulating pump {pump_id} for {dispense_time}s")
            time.sleep(dispense_time)
            return
        self.initialize_gpio()
        pin = PUMP_GPIO_PINS.get(pump_id)
        if pin is None:
            logging.error(f"No GPIO pin assigned for pump {pump_id}")
            return
        try:
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(dispense_time)
            GPIO.output(pin, GPIO.LOW)
        except Exception as e:
            logging.error(f"Error activating pump {pump_id}: {e}")

    def cleanup(self):
        if GPIO and self.gpio_initialized:
            try:
                GPIO.cleanup()
                self.gpio_initialized = False
            except Exception as e:
                logging.error(f"GPIO cleanup failed: {e}")

pump_manager = PumpManager()

class MixerWorker(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal(bool)
    message = pyqtSignal(str, str)

    def __init__(self, drink_id, scaling_factor):
        super().__init__()
        self.drink_id = drink_id
        self.scaling_factor = scaling_factor

    def run(self):
        logging.debug("Starting MixerWorker for drink_id=%s", self.drink_id)
        try:
            recipe = get_recipe_by_id(self.drink_id)
            if not recipe:
                logging.error(f"No recipe found for drink_id={self.drink_id}")
                self.finished.emit(False)
                return

            hose_assignments = load_hose_assignments()
            calibrations = load_pump_calibrations()
            bottle_volumes = load_bottle_volumes()
            ingredients = recipe['ingredients']
            total_ingredients = len(ingredients)
            completed_ingredients = 0

            for ingredient_name, base_amount in ingredients.items():
                pump_id = next((hid for hid, bev in hose_assignments.items() if bev.lower() == ingredient_name.lower()), None)
                if pump_id is None:
                    logging.error(f"Ingredient {ingredient_name} not assigned to any hose")
                    continue

                scaled_amount = base_amount * self.scaling_factor
                flow_rate = calibrations.get(pump_id, 10.0)
                current_remaining = bottle_volumes.get(pump_id, {}).get('remaining_volume_ml', 0)

                if current_remaining <= 0:
                    self.message.emit("Bottle Swap Required",
                                      f"Bottle for '{ingredient_name}' is empty. Swap and press OK.")
                    total = bottle_volumes[pump_id].get('total_volume_ml', 0)
                    bottle_volumes[pump_id]['remaining_volume_ml'] = total
                    save_bottle_volumes(bottle_volumes)
                    current_remaining = total

                if current_remaining < scaled_amount:
                    partial_time = current_remaining / flow_rate
                    pump_manager.activate_pump(pump_id, partial_time)
                    update_remaining_volume(pump_id, current_remaining)
                    bottle_volumes[pump_id]['remaining_volume_ml'] = 0

                    self.message.emit("Bottle Swap Required",
                                      f"Bottle for '{ingredient_name}' is empty. Swap and press OK.")
                    total = bottle_volumes[pump_id].get('total_volume_ml', 0)
                    bottle_volumes[pump_id]['remaining_volume_ml'] = total
                    save_bottle_volumes(bottle_volumes)

                    remaining_needed = scaled_amount - current_remaining
                    additional_time = remaining_needed / flow_rate
                    pump_manager.activate_pump(pump_id, additional_time)
                    update_remaining_volume(pump_id, remaining_needed)
                    bottle_volumes[pump_id]['remaining_volume_ml'] -= remaining_needed
                else:
                    dispense_time = scaled_amount / flow_rate
                    pump_manager.activate_pump(pump_id, dispense_time)
                    update_remaining_volume(pump_id, scaled_amount)
                    bottle_volumes[pump_id]['remaining_volume_ml'] -= scaled_amount

                completed_ingredients += 1
                self.progress.emit(float(completed_ingredients / total_ingredients))

            self.progress.emit(1.0)
            logging.info("Drink dispensing complete")
            self.finished.emit(True)
        except Exception as e:
            logging.error("Error in MixerWorker.run: %s", e)
            self.finished.emit(False)

def mix_drink(drink_id, scaling_factor=1.0, progress_callback=None, finished_callback=None):
    """Mixes the selected drink using a QThread"""
    logging.debug("Calling mix_drink with drink_id=%s", drink_id)
    worker = MixerWorker(drink_id, scaling_factor)
    if progress_callback:
        worker.progress.connect(progress_callback)
    if finished_callback:
        worker.finished.connect(finished_callback)
    worker.message.connect(lambda title, text: QMessageBox.information(None, title, text))
    worker.start()
    return worker

class CleanerWorker(QThread):
    progress = pyqtSignal(str, float)
    finished = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

    def run(self):
        logging.debug("Starting CleanerWorker")
        try:
            total_pumps = len(PUMP_GPIO_PINS)
            for i, pump_id in enumerate(PUMP_GPIO_PINS.keys(), 1):
                self.progress.emit(f"Preparing to clean Pump {pump_id}", (i - 1) / total_pumps)
                logging.info(f"Cleaning pump {pump_id} for 30 seconds")
                pump_manager.activate_pump(pump_id, 30)
                self.progress.emit(f"Finished cleaning Pump {pump_id}", i / total_pumps)
                time.sleep(1)
            logging.info("Cleaning sequence complete")
            self.finished.emit(True)
        except Exception as e:
            logging.error("Error in CleanerWorker.run: %s", e)
            self.finished.emit(False)

def clean_pumps(progress_callback=None, finished_callback=None):
    """Runs a cleaning sequence using a QThread"""
    logging.debug("Calling clean_pumps")
    worker = CleanerWorker()
    if progress_callback:
        worker.progress.connect(progress_callback)
    if finished_callback:
        worker.finished.connect(finished_callback)
    worker.start()
    return worker

def cleanup():
    logging.debug("Cleaning up GPIO")
    pump_manager.cleanup()
