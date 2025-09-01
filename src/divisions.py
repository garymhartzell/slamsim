import json
import os

DIVISIONS_FILE_RELATIVE_TO_ROOT = 'data/divisions.json'

def _get_divisions_file_path():
    """Constructs the absolute path to the divisions JSON file."""
    # Assuming the current working directory is the project root when the app runs
    return os.path.join(os.getcwd(), DIVISIONS_FILE_RELATIVE_TO_ROOT)

def load_divisions():
    """Loads all divisions from the JSON file."""
    file_path = _get_divisions_file_path()
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    except IOError:
        return []

def save_divisions(divisions_list):
    """Saves the list of divisions to the JSON file."""
    file_path = _get_divisions_file_path()
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(divisions_list, f, indent=4)
        return True
    except IOError:
        return False

def get_division_by_id(division_id):
    """Retrieves a single division by its ID."""
    divisions = load_divisions()
    for division in divisions:
        if division.get('ID') == division_id:
            return division
    return None

def add_division(division_data):
    """Adds a new division to the list."""
    divisions = load_divisions()
    if any(d.get('ID') == division_data['ID'] for d in divisions):
        return False, "Division with this ID already exists."
    divisions.append(division_data)
    if save_divisions(divisions):
        return True, "Division added successfully."
    return False, "Error saving division."

def update_division(original_id, updated_data):
    """Updates an existing division."""
    divisions = load_divisions()
    found = False
    for i, division in enumerate(divisions):
        if division.get('ID') == original_id:
            divisions[i] = updated_data
            found = True
            break
    if found:
        if save_divisions(divisions):
            return True, "Division updated successfully."
        return False, "Error saving division."
    return False, "Division not found."

def delete_division(division_id):
    """Deletes a division by its ID."""
    divisions = load_divisions()
    initial_count = len(divisions)
    divisions = [d for d in divisions if d.get('ID') != division_id]
    if len(divisions) < initial_count:
        if save_divisions(divisions):
            return True, "Division deleted successfully."
        return False, "Error saving changes."
    return False, "Division not found."

def get_division_name_by_id(division_id):
    """Returns the name of a division given its ID."""
    division = get_division_by_id(division_id)
    return division.get('Name') if division else 'Unknown Division'

def get_all_division_ids_and_names():
    """Returns a list of dictionaries with 'ID' and 'Name' for all active divisions."""
    divisions = load_divisions()
    return [{'ID': d['ID'], 'Name': d['Name']} for d in divisions if d.get('Status') == 'Active']
