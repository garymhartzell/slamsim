import json
import os
import uuid
from datetime import datetime
from src.wrestlers import load_wrestlers, save_wrestlers
from src.tagteams import load_tagteams, save_tagteams

BELTS_FILE_RELATIVE_TO_ROOT = 'data/belts.json'
BELT_HISTORY_FILE_RELATIVE_TO_ROOT = 'data/belt_history.json'

def _get_belts_file_path():
    """Constructs the absolute path to the belts JSON file."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(project_root, BELTS_FILE_RELATIVE_TO_ROOT)

def _get_belt_history_file_path():
    """Constructs the absolute path to the belt history JSON file."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(project_root, BELT_HISTORY_FILE_RELATIVE_TO_ROOT)

def load_belts():
    """Loads all belts from the JSON file."""
    file_path = _get_belts_file_path()
    if not os.path.exists(file_path): return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content) if content else []
    except (IOError, json.JSONDecodeError): return []

def save_belts(belts_list):
    """Saves the list of belts to the JSON file."""
    file_path = _get_belts_file_path()
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(belts_list, f, indent=4)
        return True
    except IOError: return False

def get_belt_by_id(belt_id):
    """Retrieves a single belt by its ID."""
    return next((belt for belt in load_belts() if belt.get('ID') == belt_id), None)

def get_belt_by_name(belt_name):
    """Retrieves a single belt by its full name, performing a case-insensitive and stripped match."""
    normalized_belt_name = belt_name.strip().lower()
    return next((belt for belt in load_belts() if belt.get('Name', '').strip().lower() == normalized_belt_name), None)

def load_active_belts_by_type(holder_type):
    """Loads all active belts of a specific type."""
    return [belt for belt in load_belts() if belt.get('Status') == 'Active' and belt.get('Holder_Type') == holder_type]

def add_belt(belt_data):
    """Adds a new belt to the list."""
    belts = load_belts()
    if any(b.get('ID') == belt_data['ID'] for b in belts):
        return False, "A belt with this ID already exists."
    belts.append(belt_data)
    return (True, "Belt added successfully.") if save_belts(belts) else (False, "Error saving belt.")

def update_belt(original_id, updated_data):
    """Updates an existing belt."""
    belts = load_belts()
    index_to_update = next((i for i, belt in enumerate(belts) if belt.get('ID') == original_id), -1)
    if index_to_update != -1:
        belts[index_to_update] = updated_data
        return (True, "Belt updated successfully.") if save_belts(belts) else (False, "Error saving belt.")
    return False, "Belt not found."

def delete_belt(belt_id):
    """Deletes a belt by its ID."""
    belts = load_belts()
    belts_after = [b for b in belts if b.get('ID') != belt_id]
    if len(belts_after) < len(belts):
        return (True, "Belt deleted successfully.") if save_belts(belts_after) else (False, "Error saving changes.")
    return False, "Belt not found."

# --- Championship History Functions ---

def load_belt_history():
    """Loads all belt history from the JSON file."""
    file_path = _get_belt_history_file_path()
    if not os.path.exists(file_path): return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return json.loads(content) if content else []
    except (IOError, json.JSONDecodeError): return []

def save_belt_history(history_list):
    """Saves the list of belt history to the JSON file."""
    file_path = _get_belt_history_file_path()
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history_list, f, indent=4)
        return True
    except IOError: return False

def load_history_for_belt(belt_id):
    """Loads all history entries for a specific belt ID."""
    return [reign for reign in load_belt_history() if reign.get('Belt_ID') == belt_id]

def get_reign_by_id(reign_id):
    """Retrieves a single reign by its unique Reign_ID."""
    return next((reign for reign in load_belt_history() if reign.get('Reign_ID') == reign_id), None)

def add_reign_to_history(reign_data):
    """Adds a new reign to the history, generating a unique ID."""
    history = load_belt_history()
    reign_data['Reign_ID'] = str(uuid.uuid4())
    history.append(reign_data)
    return (True, "Reign added to history.") if save_belt_history(history) else (False, "Error saving reign history.")

def update_reign_in_history(reign_id, updated_data):
    """Updates an existing reign in the history."""
    history = load_belt_history()
    index_to_update = next((i for i, reign in enumerate(history) if reign.get('Reign_ID') == reign_id), -1)
    if index_to_update != -1:
        history[index_to_update] = updated_data
        return (True, "Reign updated successfully.") if save_belt_history(history) else (False, "Error saving reign.")
    return False, "Reign not found."

def delete_reign_from_history(reign_id):
    """Deletes a reign from history by its Reign_ID."""
    history = load_belt_history()
    history_after = [r for r in history if r.get('Reign_ID') != reign_id]
    if len(history_after) < len(history):
        return (True, "Reign deleted successfully.") if save_belt_history(history_after) else (False, "Error saving changes.")
    return False, "Reign not found."

def process_championship_change(belt, winner_name, event_date):
    """Handles all data updates for a championship change."""
    all_belts = load_belts()
    all_wrestlers = load_wrestlers()
    all_tagteams = load_tagteams()
    history = load_belt_history()
    
    belt_id = belt['ID']
    old_champion_name = belt.get('Current_Holder')
    belt_type = belt.get('Holder_Type')

    # 1. Close the old reign in history
    if old_champion_name:
        for reign in history:
            if reign.get('Belt_ID') == belt_id and not reign.get('Date_Lost'):
                reign['Date_Lost'] = event_date
                break
    
    # 2. Create the new reign in history
    new_reign = {
        "Reign_ID": str(uuid.uuid4()), "Belt_ID": belt_id, "Champion_Name": winner_name,
        "Date_Won": event_date, "Date_Lost": None, "Defenses": 0,
        "Notes": f"Won from {old_champion_name or 'vacant status'}"
    }
    history.append(new_reign)
    save_belt_history(history)

    # 3. Update the belt's current holder in belts.json
    for b in all_belts:
        if b['ID'] == belt_id:
            b['Current_Holder'] = winner_name
            break
    save_belts(all_belts)

    # 4. Update the Belt field for the old and new champion
    if belt_type == 'Singles':
        if old_champion_name:
            for w in all_wrestlers:
                if w['Name'] == old_champion_name: w['Belt'] = ''
        for w in all_wrestlers:
            if w['Name'] == winner_name: w['Belt'] = belt['Name']
        save_wrestlers(all_wrestlers)
    elif belt_type == 'Tag-Team':
        if old_champion_name:
            for t in all_tagteams:
                if t['Name'] == old_champion_name: t['Belt'] = ''
        for t in all_tagteams:
            if t['Name'] == winner_name: t['Belt'] = belt['Name']
        save_tagteams(all_tagteams)

