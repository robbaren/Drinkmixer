# density_info.py
import os
import json
from config_manager import load_json, save_json

DENSITY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'densities.json')

DEFAULT_DENSITIES = {
    "vodka": 0.95, "gin": 0.95, "whiskey": 0.95, "tequila": 0.95, "rum": 0.95,
    "cachaca": 0.95, "triple sec": 1.00, "soda water": 1.00, "cranberry juice": 1.05,
    "lime juice": 1.03, "lemon juice": 1.03, "sugar syrup": 1.30, "cola": 1.03,
    "tonic water": 1.02, "coffee liqueur": 1.20, "pineapple juice": 1.04,
    "coconut cream": 1.10, "orgeat syrup": 1.20, "coffee": 1.00, "champagne": 0.99,
    "cognac": 0.96, "amaretto": 1.02, "absinthe": 0.92, "apple brandy": 0.96,
    "vermouth": 1.00, "elderflower liqueur": 1.00, "sake": 1.00
}
DENSITY_INFO = load_json(DENSITY_FILE, DEFAULT_DENSITIES)

def get_density(liquid_name):
    """Returns the density for the given liquid name (case-insensitive)"""
    return DENSITY_INFO.get(liquid_name.lower(), 1.0)

def add_density(liquid_name, density):
    """Add a new density and persist it"""
    if not isinstance(density, (int, float)) or density <= 0:
        raise ValueError("Density must be a positive number")
    DENSITY_INFO[liquid_name.lower()] = float(density)
    save_json(DENSITY_INFO, DENSITY_FILE)
