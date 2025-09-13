import json
import os

WRESTLERS_FILE_RELATIVE_TO_ROOT = 'data/wrestlers.json'

def _get_wrestlers_file_path():
    """Constructs the absolute path to the wrestlers data file."""
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
    return next((w for w in load_wrestlers() if w.get('Name') == name), None)

def add_wrestler(wrestler_data):
    """Adds a new wrestler to the data."""
    wrestlers = load_wrestlers()
    if any(w.get('Name') == wrestler_data.get('Name') for w in wrestlers):
        return False
    wrestlers.append(wrestler_data)
    save_wrestlers(wrestlers)
    return True

def update_wrestler(original_name, updated_data):
    """Updates an existing wrestler's data."""
    wrestlers = load_wrestlers()
    index_to_update = next((i for i, w in enumerate(wrestlers) if w.get('Name') == original_name), -1)
    if index_to_update != -1:
        if original_name != updated_data.get('Name') and any(w.get('Name') == updated_data.get('Name') for w in wrestlers):
            return False
        wrestlers[index_to_update] = updated_data
        save_wrestlers(wrestlers)
        return True
    return False

def delete_wrestler(name):
    """Deletes a wrestler by their unique name."""
    wrestlers = load_wrestlers()
    wrestlers_after = [w for w in wrestlers if w.get('Name') != name]
    if len(wrestlers_after) < len(wrestlers):
        save_wrestlers(wrestlers_after)
        return True
    return False

def update_wrestler_record(wrestler_name, match_class, result):
    """Updates a wrestler's win/loss/draw record for a given match type."""
    all_wrestlers = load_wrestlers()
    wrestler_found = False
    for wrestler in all_wrestlers:
        if wrestler['Name'] == wrestler_name:
            wrestler_found = True
            if match_class == 'singles':
                if result == 'Win': wrestler['Singles_Wins'] = str(int(wrestler.get('Singles_Wins', 0)) + 1)
                elif result == 'Loss': wrestler['Singles_Losses'] = str(int(wrestler.get('Singles_Losses', 0)) + 1)
                elif result == 'Draw': wrestler['Singles_Draws'] = str(int(wrestler.get('Singles_Draws', 0)) + 1)
            elif match_class in ['tag', 'other', 'battle_royal']:
                if result == 'Win': wrestler['Tag_Wins'] = str(int(wrestler.get('Tag_Wins', 0)) + 1)
                elif result == 'Loss': wrestler['Tag_Losses'] = str(int(wrestler.get('Tag_Losses', 0)) + 1)
                elif result == 'Draw': wrestler['Tag_Draws'] = str(int(wrestler.get('Tag_Draws', 0)) + 1)
            break
    if wrestler_found: save_wrestlers(all_wrestlers)
    return wrestler_found

def update_wrestler_team_affiliation(wrestler_name, team_name):
    """Sets or clears a wrestler's team affiliation."""
    all_wrestlers = load_wrestlers()
    for wrestler in all_wrestlers:
        if wrestler['Name'] == wrestler_name:
            wrestler['Team'] = team_name
            break
    save_wrestlers(all_wrestlers)

def reset_all_wrestler_records():
    """Sets all win/loss/draw records for every wrestler to 0."""
    all_wrestlers = load_wrestlers()
    for wrestler in all_wrestlers:
        wrestler['Singles_Wins'] = '0'
        wrestler['Singles_Losses'] = '0'
        wrestler['Singles_Draws'] = '0'
        wrestler['Tag_Wins'] = '0'
        wrestler['Tag_Losses'] = '0'
        wrestler['Tag_Draws'] = '0'
    save_wrestlers(all_wrestlers)

