import json
import os

BELTS_FILE_RELATIVE_TO_ROOT = 'data/belts.json'

def _get_belts_file_path():
    """Constructs the absolute path to the belts JSON file."""
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, os.pardir))
    return os.path.join(project_root, BELTS_FILE_RELATIVE_TO_ROOT)

def load_belts():
    """Loads all belts from the JSON file."""
    file_path = _get_belts_file_path()
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except (IOError, json.JSONDecodeError):
        return []

def save_belts(belts_list):
    """Saves the list of belts to the JSON file."""
    file_path = _get_belts_file_path()
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(belts_list, f, indent=4)
        return True
    except IOError:
        return False

def get_belt_by_id(belt_id):
    """Retrieves a single belt by its ID."""
    belts = load_belts()
    for belt in belts:
        if belt.get('ID') == belt_id:
            return belt
    return None

def load_active_belts_by_type(holder_type):
    """Loads all active belts of a specific type (Singles or Tag-Team)."""
    all_belts = load_belts()
    return [
        belt for belt in all_belts 
        if belt.get('Status') == 'Active' and belt.get('Holder_Type') == holder_type
    ]

def add_belt(belt_data):
    """Adds a new belt to the list."""
    belts = load_belts()
    if any(b.get('ID') == belt_data['ID'] for b in belts):
        return False, "A belt with this ID already exists."
    belts.append(belt_data)
    if save_belts(belts):
        return True, "Belt added successfully."
    return False, "Error saving belt."

def update_belt(original_id, updated_data):
    """Updates an existing belt."""
    belts = load_belts()
    found = False
    for i, belt in enumerate(belts):
        if belt.get('ID') == original_id:
            belts[i] = updated_data
            found = True
            break
    if found and save_belts(belts):
        return True, "Belt updated successfully."
    elif not found:
        return False, "Belt not found."
    else:
        return False, "Error saving belt."

def delete_belt(belt_id):
    """Deletes a belt by its ID."""
    belts = load_belts()
    initial_count = len(belts)
    belts = [b for b in belts if b.get('ID') != belt_id]
    if len(belts) < initial_count and save_belts(belts):
        return True, "Belt deleted successfully."
    elif len(belts) == initial_count:
        return False, "Belt not found."
    else:
        return False, "Error saving changes."

