# controller.py
import logging
from drink_mixer import mix_drink, clean_pumps
from recipe_manager import load_all_recipes, get_recipe_by_id, save_recipe, delete_recipe
from config_manager import (
    load_hose_assignments, load_hose_statuses, load_bottle_volumes, get_low_volume_hoses,
    save_hose_assignments, save_hose_statuses, save_bottle_volumes
)
from calibration_manager import start_calibration, stop_calibration, prime_pump, check_density

class DrinkMixerController:
    def __init__(self):
        logging.debug("Initializing DrinkMixerController")
        try:
            self.hose_assignments = load_hose_assignments()
            self.hose_statuses = load_hose_statuses()
            self.bottle_volumes = load_bottle_volumes()
        except Exception as e:
            logging.error("Error in DrinkMixerController.__init__: %s", e)
            raise

    def get_available_drinks(self):
        logging.debug("Getting available drinks")
        try:
            return load_all_recipes()  # Use all recipes for simplicity, filter in UI if needed
        except Exception as e:
            logging.error("Error in get_available_drinks: %s", e)
            return []

    def get_recipe_by_id(self, drink_id):
        logging.debug("Getting recipe by ID: %s", drink_id)
        try:
            return get_recipe_by_id(drink_id)
        except Exception as e:
            logging.error("Error in get_recipe_by_id: %s", e)
            return None

    def mix_drink(self, drink_id, size, progress_callback, finished_callback):
        logging.debug("Mixing drink: drink_id=%s, size=%s", drink_id, size)
        try:
            recipe = self.get_recipe_by_id(drink_id)
            if not recipe:
                return None
            base_total = sum(recipe['ingredients'].values())
            scaling_factor = size / base_total
            return mix_drink(drink_id, scaling_factor, progress_callback, finished_callback)
        except Exception as e:
            logging.error("Error in mix_drink: %s", e)
            return None

    def clean_pumps(self, progress_callback, finished_callback):
        logging.debug("Cleaning pumps")
        try:
            return clean_pumps(progress_callback, finished_callback)
        except Exception as e:
            logging.error("Error in clean_pumps: %s", e)
            return None

    def save_recipe(self, drink_id, name, ingredients, notes):
        logging.debug("Saving recipe: drink_id=%s", drink_id)
        try:
            save_recipe(drink_id, name, ingredients, notes)
        except Exception as e:
            logging.error("Error in save_recipe: %s", e)

    def delete_recipe(self, drink_id):
        logging.debug("Deleting recipe: drink_id=%s", drink_id)
        try:
            delete_recipe(drink_id)
        except Exception as e:
            logging.error("Error in delete_recipe: %s", e)

    def get_hose_status(self):
        logging.debug("Getting hose status")
        try:
            return self.hose_statuses
        except Exception as e:
            logging.error("Error in get_hose_status: %s", e)
            return {}

    def get_bottle_volumes(self):
        logging.debug("Getting bottle volumes")
        try:
            return self.bottle_volumes
        except Exception as e:
            logging.error("Error in get_bottle_volumes: %s", e)
            return {}

    def get_low_volume_hoses(self):
        logging.debug("Getting low volume hoses")
        try:
            return get_low_volume_hoses()
        except Exception as e:
            logging.error("Error in get_low_volume_hoses: %s", e)
            return {}

    def get_hose_assignments(self):
        logging.debug("Getting hose assignments")
        try:
            return self.hose_assignments
        except Exception as e:
            logging.error("Error in get_hose_assignments: %s", e)
            return {}

    def update_hose_assignments(self, assignments):
        logging.debug("Updating hose assignments")
        try:
            save_hose_assignments(assignments)
            self.hose_assignments = assignments
        except Exception as e:
            logging.error("Error in update_hose_assignments: %s", e)

    def update_hose_statuses(self, statuses):
        logging.debug("Updating hose statuses")
        try:
            save_hose_statuses(statuses)
            self.hose_statuses = statuses
        except Exception as e:
            logging.error("Error in update_hose_statuses: %s", e)

    def update_bottle_volumes(self, volumes):
        logging.debug("Updating bottle volumes")
        try:
            save_bottle_volumes(volumes)
            self.bottle_volumes = volumes
        except Exception as e:
            logging.error("Error in update_bottle_volumes: %s", e)

    def start_calibration(self, pump_id):
        logging.debug("Starting calibration for pump_id=%s", pump_id)
        try:
            start_calibration(pump_id)
        except Exception as e:
            logging.error("Error in start_calibration: %s", e)

    def stop_calibration(self, pump_id, volume):
        logging.debug("Stopping calibration for pump_id=%s", pump_id)
        try:
            stop_calibration(pump_id, volume)
        except Exception as e:
            logging.error("Error in stop_calibration: %s", e)

    def prime_pump(self, pump_id):
        logging.debug("Priming pump_id=%s", pump_id)
        try:
            prime_pump(pump_id)
        except Exception as e:
            logging.error("Error in prime_pump: %s", e)

    def check_density(self, pump_id, beverage):
        logging.debug("Checking density for pump_id=%s, beverage=%s", pump_id, beverage)
        try:
            return check_density(pump_id, beverage)
        except Exception as e:
            logging.error("Error in check_density: %s", e)
            return False
