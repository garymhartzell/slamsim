from flask import Blueprint, render_template
from src.prefs import load_preferences
from src.wrestlers import load_wrestlers
from src.tagteams import load_tagteams
from src.divisions import load_divisions

fan_bp = Blueprint('fan', __name__, url_prefix='/fan')

@fan_bp.route('/home')
def home():
    """Renders the fan home page."""
    return render_template('fan/home.html')

@fan_bp.route('/roster')
def roster():
    """Renders the fan roster page with sorted wrestlers and tag teams."""
    prefs = load_preferences()
    all_wrestlers = load_wrestlers()
    all_tagteams = load_tagteams()
    all_divisions = load_divisions()

    active_wrestlers = [w for w in all_wrestlers if w.get('Status') == 'Active']
    active_tagteams = [tt for tt in all_tagteams if tt.get('Status') == 'Active']

    # Prepare a dictionary to hold roster data, grouped by division
    # Sort divisions by name for consistent display
    sorted_divisions = sorted(all_divisions, key=lambda d: d.get('Name', ''))
    
    roster_by_division = {}
    for division in sorted_divisions:
        division_id = division.get('ID')
        division_name = division.get('Name')
        roster_by_division[division_name] = {'wrestlers': [], 'tagteams': []}

        # Add wrestlers to their division
        for wrestler in active_wrestlers:
            if wrestler.get('Division') == division_id:
                roster_by_division[division_name]['wrestlers'].append(wrestler)
        
        # Add tag teams to their division
        for tagteam in active_tagteams:
            if tagteam.get('Division') == division_id:
                roster_by_division[division_name]['tagteams'].append(tagteam)

    # Sorting logic
    sort_order = prefs.get('fan_mode_roster_sort_order', 'Alphabetical')

    for division_name, data in roster_by_division.items():
        # Sort wrestlers
        if sort_order == 'Alphabetical':
            data['wrestlers'].sort(key=lambda w: w.get('Name', ''))
        elif sort_order == 'Total Wins':
            data['wrestlers'].sort(key=lambda w: (int(w.get('Singles_Wins', 0)) + int(w.get('Tag_Wins', 0))), reverse=True)
        elif sort_order == 'Win Percentage':
            def get_wrestler_win_percentage_key(wrestler):
                wins = int(wrestler.get('Singles_Wins', 0)) + int(wrestler.get('Tag_Wins', 0))
                losses = int(wrestler.get('Singles_Losses', 0)) + int(wrestler.get('Tag_Losses', 0))
                total_matches = wins + losses
                # If less than 5 matches or 0-0 record, sort alphabetically at the bottom
                if total_matches < 5 or (wins == 0 and losses == 0):
                    return (-1.0, wrestler.get('Name', '')) # -1.0 ensures it's at the bottom when sorting descending
                return (wins / total_matches, wrestler.get('Name', '')) # Win percentage, then name for tie-breaking
            data['wrestlers'].sort(key=get_wrestler_win_percentage_key, reverse=True)

        # Sort tag teams
        if sort_order == 'Alphabetical':
            data['tagteams'].sort(key=lambda tt: tt.get('Name', ''))
        elif sort_order == 'Total Wins':
            data['tagteams'].sort(key=lambda tt: int(tt.get('Wins', 0)), reverse=True)
        elif sort_order == 'Win Percentage':
            def get_tagteam_win_percentage_key(tagteam):
                wins = int(tagteam.get('Wins', 0))
                losses = int(tagteam.get('Losses', 0))
                total_matches = wins + losses
                # If less than 5 matches or 0-0 record, sort alphabetically at the bottom
                if total_matches < 5 or (wins == 0 and losses == 0):
                    return (-1.0, tagteam.get('Name', ''))
                return (wins / total_matches, tagteam.get('Name', ''))
            data['tagteams'].sort(key=get_tagteam_win_percentage_key, reverse=True)

    # Filter out divisions that have no active wrestlers or tagteams
    filtered_roster_by_division = {
        div_name: data for div_name, data in roster_by_division.items()
        if data['wrestlers'] or data['tagteams']
    }

    return render_template('fan/roster.html', roster_data=filtered_roster_by_division, prefs=prefs)
