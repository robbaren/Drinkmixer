# calibration_manager.py
import time
import logging
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

from config_manager import save_pump_calibration
from drink_mixer import PUMP_GPIO_PINS
from density_info import get_density

CALIBRATION_SESSIONS = {}

def start_calibration(pump_id):
    """Records the start time and activates the pump"""
    if pump_id in CALIBRATION_SESSIONS:
        logging.warning(f"Pump {pump_id} is already in calibration mode!")
        return
    CALIBRATION_SESSIONS[pump_id] = {'start_time': time.time()}
    pin = PUMP_GPIO_PINS.get(pump_id)
    if pin and GPIO:
        try:
            GPIO.output(pin, GPIO.HIGH)
        except Exception as e:
            logging.error(f"Error starting pump {pump_id}: {e}")
    logging.info(f"Calibration started for pump {pump_id}...")

def stop_calibration(pump_id, dispensed_volume_ml):
    """Stops calibration and saves flow rate"""
    if pump_id not in CALIBRATION_SESSIONS:
        logging.error(f"Pump {pump_id} was not in calibration mode!")
        return
    pin = PUMP_GPIO_PINS.get(pump_id)
    if pin and GPIO:
        try:
            GPIO.output(pin, GPIO.LOW)
        except Exception as e:
            logging.error(f"Error stopping pump {pump_id}: {e}")
    start_time = CALIBRATION_SESSIONS[pump_id]['start_time']
    elapsed = time.time() - start_time
    flow_rate = calculate_flow_rate(elapsed, dispensed_volume_ml)
    save_pump_calibration(pump_id, flow_rate)
    logging.info(f"Calibration complete for pump {pump_id}: Flow rate = {flow_rate:.2f} ml/s")
    del CALIBRATION_SESSIONS[pump_id]

def calculate_flow_rate(elapsed_time_s, dispensed_volume_ml):
    if elapsed_time_s <= 0 or dispensed_volume_ml < 0:
        return 0
    return dispensed_volume_ml / elapsed_time_s

def prime_pump(pump_id, prime_duration=1.0):
    """Activates the pump briefly to prime it"""
    pin = PUMP_GPIO_PINS.get(pump_id)
    if not pin or not GPIO:
        logging.error(f"No GPIO pin assigned or GPIO unavailable for pump {pump_id}")
        return
    logging.info(f"Priming pump {pump_id} for {prime_duration} seconds...")
    try:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(prime_duration)
        GPIO.output(pin, GPIO.LOW)
        logging.info(f"Pump {pump_id} primed")
    except Exception as e:
        logging.error(f"Error priming pump {pump_id}: {e}")

def check_density(pump_id, new_beverage):
    """Checks if the new beverage's density matches the expected"""
    from config_manager import load_hose_assignments
    hose_assignments = load_hose_assignments()
    expected = hose_assignments.get(pump_id, "").lower().strip()
    new_beverage_lower = new_beverage.lower().strip()
    expected_density = get_density(expected)
    new_density = get_density(new_beverage_lower)
    logging.info(f"Expected density for '{expected}': {expected_density} g/ml, new density for '{new_beverage_lower}': {new_density} g/ml")
    return abs(expected_density - new_density) <= 0.05
