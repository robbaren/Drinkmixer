# availability_checker.py
from config_manager import load_hose_assignments, load_hose_statuses
from recipe_manager import load_all_recipes
import logging

def get_available_drinks():
    """Returns a list of drink dictionaries that can be made with current hoses and statuses"""
    hose_assignments = load_hose_assignments()
    hose_statuses = load_hose_statuses()
    recipes = load_all_recipes()
    available_drinks = []
    for recipe in recipes:
        if is_drink_available(recipe, hose_assignments, hose_statuses):
            available_drinks.append(recipe)
    return available_drinks

def is_drink_available(drink, hose_assignments, hose_statuses):
    """Check if all ingredients are assigned to non-empty hoses"""
    for ingredient in drink['ingredients'].keys():
        matched_hose = None
        for hose_id, beverage_name in hose_assignments.items():
            if beverage_name.lower() == ingredient.lower():
                matched_hose = hose_id
                break
        if matched_hose is None or hose_statuses.get(matched_hose, True):
            return False
    return True
