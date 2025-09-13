import json
import os
from src.wrestlers import get_wrestler_by_name

TAGTEAMS_FILE_RELATIVE_TO_ROOT = 'data/tagteams.json'

def _get_tagteams_file_path():
    """Constructs the absolute path to the tagteams data file."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(project_root, TAGTEAMS_FILE_RELATIVE_TO_ROOT)

def load_tagteams():
    """Loads tag-team data from the JSON file."""
    filepath = _get_tagteams_file_path()
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
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
    return next((tt for tt in load_tagteams() if tt['Name'] == name), None)

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
    tagteams = [tt for tt in load_tagteams() if tt['Name'] != name]
    save_tagteams(tagteams)

def get_wrestler_names():
    """Returns a list of all wrestler names."""
    from src.wrestlers import load_wrestlers
    return sorted([w['Name'] for w in load_wrestlers()])

def get_active_members_status(member_names):
    """Checks if all specified members are active."""
    for member_name in member_names:
        if member_name:
            wrestler = get_wrestler_by_name(member_name)
            if wrestler and wrestler.get('Status') != 'Active':
                return False
    return True

def update_tagteam_record(team_name, result):
    """Updates a tag team's win/loss/draw record."""
    all_tagteams = load_tagteams()
    team_found = False
    for team in all_tagteams:
        if team['Name'] == team_name:
            team_found = True
            if result == 'Win':
                team['Wins'] = str(int(team.get('Wins', 0)) + 1)
            elif result == 'Loss':
                team['Losses'] = str(int(team.get('Losses', 0)) + 1)
            elif result == 'Draw':
                team['Draws'] = str(int(team.get('Draws', 0)) + 1)
            break
    if team_found:
        save_tagteams(all_tagteams)
    return team_found

def reset_all_tagteam_records():
    """Sets all win/loss/draw records for every tag team to 0."""
    all_tagteams = load_tagteams()
    for team in all_tagteams:
        team['Wins'] = '0'
        team['Losses'] = '0'
        team['Draws'] = '0'
    save_tagteams(all_tagteams)

