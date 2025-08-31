import json
import os

WRESTLERS_FILE_RELATIVE_TO_ROOT = 'data/wrestlers.json'

def _get_wrestlers_file_path():
    """Constructs the absolute path to the wrestlers data file, relative to the project root."""
    # __file__ is src/wrestlers.py
    # os.path.dirname(__file__) is src/
    # os.path.join(os.path.dirname(__file__), '..') is the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(project_root, WRESTLERS_FILE_RELATIVE_TO_ROOT)

def load_wrestlers():
    """Loads wrestler data from the JSON file."""
    file_path = _get_wrestlers_file_path()
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_wrestlers(wrestlers_list):
    """Saves wrestler data to the JSON file."""
    file_path = _get_wrestlers_file_path()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(wrestlers_list, f, indent=4)

def get_wrestler_by_name(name):
    """Retrieves a wrestler by their unique name."""
    wrestlers = load_wrestlers()
    for wrestler in wrestlers:
        if wrestler.get('Name') == name:
            return wrestler
    return None

def add_wrestler(wrestler_data):
    """Adds a new wrestler to the data. Returns True on success, False if wrestler name already exists."""
    wrestlers = load_wrestlers()
    if any(w.get('Name') == wrestler_data.get('Name') for w in wrestlers):
        return False # Wrestler with this name already exists
    wrestlers.append(wrestler_data)
    save_wrestlers(wrestlers)
    return True

def update_wrestler(original_name, updated_data):
    """Updates an existing wrestler's data. Returns True on success, False if wrestler not found or new name conflicts."""
    wrestlers = load_wrestlers()
    for i, wrestler in enumerate(wrestlers):
        if wrestler.get('Name') == original_name:
            # Check if the name itself was changed and if the new name conflicts with another wrestler
            if original_name != updated_data.get('Name') and any(w.get('Name') == updated_data.get('Name') for w in wrestlers if w.get('Name') != original_name):
                return False # New name conflicts with existing wrestler
            wrestlers[i] = updated_data
            save_wrestlers(wrestlers)
            return True
    return False

def delete_wrestler(name):
    """Deletes a wrestler by their unique name. Returns True on success, False if wrestler not found."""
    wrestlers = load_wrestlers()
    original_len = len(wrestlers)
    wrestlers = [w for w in wrestlers if w.get('Name') != name]
    if len(wrestlers) < original_len:
        save_wrestlers(wrestlers)
        return True
    return False
