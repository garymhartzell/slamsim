import json
import os

PREFS_FILE = 'data/prefs.json'

def _get_prefs_file_path():
    """Constructs the absolute path to the preferences file."""
    # Assuming data/prefs.json is relative to the project root
    # For now, it's relative to where the app is run from, adjust if needed.
    return os.path.join(os.getcwd(), PREFS_FILE)

def load_preferences():
    """
    Loads preferences from data/prefs.json.
    Returns a dictionary of preferences, with default values if the file is not found
    or specific preferences are missing.
    """
    prefs_path = _get_prefs_file_path()
    prefs_data = {}
    default_prefs = {
        "league_name": "Fantasy Elite Wrestling",
        "league_short": "FEW"
    }

    if os.path.exists(prefs_path):
        try:
            with open(prefs_path, 'r', encoding='utf-8') as f:
                json_list = json.load(f)
                for item in json_list:
                    if 'Pref' in item and 'Value' in item:
                        key = item['Pref'].lower() # Convert to lowercase for consistent access
                        prefs_data[key] = item['Value']
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {prefs_path}. Using default preferences.")
            prefs_data = {} # Reset to empty to be filled by defaults

    # Merge with defaults to ensure all expected preferences are present
    final_prefs = default_prefs.copy()
    final_prefs.update(prefs_data)
    
    return final_prefs

def save_preferences(prefs_dict):
    """
    Saves preferences to data/prefs.json.
    Expects a dictionary like {'league_name': '...', 'league_short': '...'}.
    """
    prefs_path = _get_prefs_file_path()
    
    # Convert back to the list of dictionaries format for saving
    json_list = [
        {"Pref": "League_Name", "Value": prefs_dict.get("league_name", "")},
        {"Pref": "League_Short", "Value": prefs_dict.get("league_short", "")}
    ]

    os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(json_list, f, indent=4)
