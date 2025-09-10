import json
import os
from src.wrestlers import load_wrestlers
from src.tagteams import load_tagteams

DIVISIONS_FILE_RELATIVE_TO_ROOT = 'data/divisions.json'

def _get_divisions_file_path():
    """Constructs the absolute path to the divisions JSON file."""
    return os.path.join(os.getcwd(), DIVISIONS_FILE_RELATIVE_TO_ROOT)

def load_divisions():
    """Loads all divisions from the JSON file."""
    file_path = _get_divisions_file_path()
    if not os.path.exists(file_path): return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content) if content else []
    except (IOError, json.JSONDecodeError): return []

def save_divisions(divisions_list):
    """Saves the list of divisions to the JSON file."""
    file_path = _get_divisions_file_path()
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(divisions_list, f, indent=4)
        return True
    except IOError: return False

def get_division_by_id(division_id):
    """Retrieves a single division by its ID."""
    return next((d for d in load_divisions() if d.get('ID') == division_id), None)

def add_division(division_data):
    """Adds a new division to the list."""
    divisions = load_divisions()
    if any(d.get('ID') == division_data['ID'] for d in divisions):
        return False, "Division with this ID already exists."
    divisions.append(division_data)
    return (True, "Division added successfully.") if save_divisions(divisions) else (False, "Error saving division.")

def update_division(original_id, updated_data):
    """Updates an existing division."""
    divisions = load_divisions()
    index = next((i for i, d in enumerate(divisions) if d.get('ID') == original_id), -1)
    if index != -1:
        divisions[index] = updated_data
        return (True, "Division updated successfully.") if save_divisions(divisions) else (False, "Error saving division.")
    return False, "Division not found."

def delete_division(division_id):
    """Deletes a division by its ID."""
    divisions = load_divisions()
    divisions_after = [d for d in divisions if d.get('ID') != division_id]
    if len(divisions_after) < len(divisions):
        return (True, "Division deleted successfully.") if save_divisions(divisions_after) else (False, "Error saving changes.")
    return False, "Division not found."

def get_division_name_by_id(division_id):
    """Returns the name of a division given its ID."""
    division = get_division_by_id(division_id)
    return division.get('Name') if division else 'Unknown Division'

def get_all_division_ids_and_names():
    """Returns a list of dictionaries with 'ID' and 'Name' for all active divisions."""
    return [{'ID': d['ID'], 'Name': d['Name']} for d in load_divisions() if d.get('Status') == 'Active']

def is_division_in_use(division_id):
    """Checks if any wrestler or tag team is currently assigned to this division."""
    all_wrestlers = load_wrestlers()
    if any(w.get('Division') == division_id for w in all_wrestlers):
        return True

    all_tagteams = load_tagteams()
    return any(t.get('Division') == division_id for t in all_tagteams)

