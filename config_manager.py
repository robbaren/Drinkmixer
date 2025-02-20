# config_manager.py
import os
import json
import logging
from threading import Lock

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

HOSE_ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'hose_assignments.json')
PUMP_CALIBRATIONS_FILE = os.path.join(DATA_DIR, 'pump_calibrations.json')
HOSE_STATUSES_FILE = os.path.join(DATA_DIR, 'hose_statuses.json')
BOTTLE_VOLUMES_FILE = os.path.join(DATA_DIR, 'bottle_volumes.json')

file_lock = Lock()

def load_json(file_path, default):
    with file_lock:
        if not os.path.exists(file_path):
            return default
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            logging.error(f"Error loading {file_path}: {e}")
            return default

def save_json(data, file_path):
    with file_lock:
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving {file_path}: {e}")

def load_hose_assignments():
    """Returns a dict {hose_id (int): beverage_name (str)}"""
    data = load_json(HOSE_ASSIGNMENTS_FILE, {})
    return {int(k): str(v) for k, v in data.items() if isinstance(k, (int, str)) and isinstance(v, str)}

def save_hose_assignments(assignments):
    save_json({str(k): v for k, v in assignments.items()}, HOSE_ASSIGNMENTS_FILE)

def load_pump_calibrations():
    """Returns a dict {pump_id (int): flow_rate_ml_per_sec (float)}"""
    data = load_json(PUMP_CALIBRATIONS_FILE, {})
    return {int(k): float(v) for k, v in data.items() if isinstance(k, (int, str)) and isinstance(v, (int, float))}

def save_pump_calibration(pump_id, flow_rate):
    if not isinstance(flow_rate, (int, float)) or flow_rate < 0:
        raise ValueError("Flow rate must be a non-negative number")
    calibrations = load_pump_calibrations()
    calibrations[int(pump_id)] = float(flow_rate)
    save_json(calibrations, PUMP_CALIBRATIONS_FILE)

def load_hose_statuses():
    """Returns a dict {hose_id (int): is_empty (bool)}"""
    data = load_json(HOSE_STATUSES_FILE, {})
    return {int(k): bool(v) for k, v in data.items() if isinstance(k, (int, str))}

def save_hose_statuses(statuses):
    save_json({str(k): v for k, v in statuses.items()}, HOSE_STATUSES_FILE)

def load_bottle_volumes():
    """Returns a dict {hose_id (int): {'total_volume_ml': int, 'remaining_volume_ml': int}}"""
    data = load_json(BOTTLE_VOLUMES_FILE, {})
    volumes = {}
    for k, v in data.items():
        try:
            hose_id = int(k)
            volumes[hose_id] = {
                'total_volume_ml': int(v.get('total_volume_ml', 0)),
                'remaining_volume_ml': int(v.get('remaining_volume_ml', 0))
            }
        except Exception as e:
            logging.error(f"Error processing bottle volume for hose {k}: {e}")
    return volumes

def save_bottle_volumes(volumes):
    data = {str(k): v for k, v in volumes.items()}
    save_json(data, BOTTLE_VOLUMES_FILE)

def update_remaining_volume(hose_id, dispensed_volume):
    """Subtract dispensed_volume (ml) from the hose_id's remaining_volume_ml"""
    if not isinstance(dispensed_volume, (int, float)) or dispensed_volume < 0:
        raise ValueError("Dispensed volume must be a non-negative number")
    volumes = load_bottle_volumes()
    if hose_id in volumes:
        volumes[hose_id]['remaining_volume_ml'] = max(
            0, volumes[hose_id]['remaining_volume_ml'] - dispensed_volume
        )
    save_bottle_volumes(volumes)

def get_low_volume_hoses(threshold=0.1):  # 10% threshold
    """Returns dict of hoses with low volume {hose_id: remaining_fraction}"""
    volumes = load_bottle_volumes()
    return {
        hose_id: vol['remaining_volume_ml'] / vol['total_volume_ml']
        for hose_id, vol in volumes.items()
        if vol['total_volume_ml'] > 0 and vol['remaining_volume_ml'] / vol['total_volume_ml'] <= threshold
    }
