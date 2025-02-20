# recipe_manager.py
import os
import json
import logging
from config_manager import load_json, save_json

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
RECIPE_FILE = os.path.join(DATA_DIR, 'drink_recipes.json')

def load_all_recipes():
    """Returns a list of recipe dictionaries"""
    recipes = load_json(RECIPE_FILE, [])
    processed = []
    for recipe in recipes:
        try:
            processed.append({
                'drink_id': int(recipe['drink_id']),
                'drink_name': str(recipe['drink_name']),
                'ingredients': {str(k): int(v) for k, v in recipe.get('ingredients', {}).items()},
                'notes': str(recipe.get('notes', ''))
            })
        except Exception as e:
            logging.error(f"Error processing recipe {recipe}: {e}")
    return processed

def get_recipe_by_id(drink_id):
    all_recipes = load_all_recipes()
    for recipe in all_recipes:
        if recipe.get('drink_id') == drink_id:
            return recipe
    return None

def save_recipe(drink_id, drink_name, ingredients, notes):
    """Save or update a recipe"""
    recipes = load_all_recipes()
    recipe = next((r for r in recipes if r['drink_id'] == drink_id), None)
    if recipe:
        recipe.update({'drink_name': drink_name, 'ingredients': ingredients, 'notes': notes})
    else:
        recipes.append({'drink_id': drink_id, 'drink_name': drink_name, 'ingredients': ingredients, 'notes': notes})
    save_json(recipes, RECIPE_FILE)

def delete_recipe(drink_id):
    """Delete a recipe by ID"""
    recipes = load_all_recipes()
    recipes = [r for r in recipes if r['drink_id'] != drink_id]
    save_json(recipes, RECIPE_FILE)
