import json
import os
from flask import current_app
from src.wrestlers import load_wrestlers, get_wrestler_by_name

TAGTEAMS_FILE_RELATIVE_TO_ROOT = 'data/tagteams.json'

def _get_tagteams_file_path():
    """Constructs the absolute path to the tagteams data file."""
    return os.path.join(current_app.root_path, '..', TAGTEAMS_FILE_RELATIVE_TO_ROOT)

def load_tagteams():
    """Loads tag-team data from the JSON file."""
    filepath = _get_tagteams_file_path()
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tagteams(tagteams_list):
    """Saves tag-team data to the JSON file."""
    filepath = _get_tagteams_file_path()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tagteams_list, f, indent=4)

def get_tagteam_by_name(name):
    """Retrieves a single tag-team by its name."""
    tagteams = load_tagteams()
    return next((tt for tt in tagteams if tt['Name'] == name), None)

def add_tagteam(tagteam_data):
    """Adds a new tag-team to the list."""
    tagteams = load_tagteams()
    tagteams.append(tagteam_data)
    save_tagteams(tagteams)

def update_tagteam(original_name, updated_data):
    """Updates an existing tag-team's data."""
    tagteams = load_tagteams()
    for i, tt in enumerate(tagteams):
        if tt['Name'] == original_name:
            tagteams[i] = updated_data
            break
    save_tagteams(tagteams)

def delete_tagteam(name):
    """Deletes a tag-team by its name."""
    tagteams = load_tagteams()
    tagteams = [tt for tt in tagteams if tt['Name'] != name]
    save_tagteams(tagteams)

def get_wrestler_names():
    """Returns a list of all wrestler names."""
    wrestlers = load_wrestlers()
    return sorted([w['Name'] for w in wrestlers])

def get_active_members_status(member_names):
    """Checks if all specified members are active."""
    wrestlers = load_wrestlers()
    for member_name in member_names:
        if member_name: # Ensure member_name is not empty
            wrestler = get_wrestler_by_name(member_name)
            if wrestler and wrestler.get('Status') != 'Active':
                return False
    return True
