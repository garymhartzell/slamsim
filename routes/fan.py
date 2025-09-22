from flask import Blueprint, render_template, flash, redirect, url_for
from src.prefs import load_preferences
from src.wrestlers import load_wrestlers, get_wrestler_by_name
from src.tagteams import load_tagteams, get_tagteam_by_name
from src.divisions import load_divisions
from src.events import get_event_by_name, load_event_summary_content, get_event_by_slug
from src.segments import load_segments, get_match_by_id, _slugify # Import _slugify for event_slug

fan_bp = Blueprint('fan', __name__, url_prefix='/fan')

@fan_bp.route('/home')
def home():
    """Renders the fan home page."""
    return render_template('fan/home.html')

@fan_bp.route('/wrestler/<string:wrestler_name>')
def view_wrestler(wrestler_name):
    """Renders the fan view page for a specific wrestler."""
    prefs = load_preferences()
    wrestler = get_wrestler_by_name(wrestler_name)

    if not wrestler:
        flash(f"Wrestler '{wrestler_name}' not found.", 'danger')
        return redirect(url_for('fan.roster'))

    # Calculate total record
    singles_wins = int(wrestler.get('Singles_Wins', 0))
    singles_losses = int(wrestler.get('Singles_Losses', 0))
    singles_draws = int(wrestler.get('Singles_Draws', 0))
    tag_wins = int(wrestler.get('Tag_Wins', 0))
    tag_losses = int(wrestler.get('Tag_Losses', 0))
    tag_draws = int(wrestler.get('Tag_Draws', 0))

    total_record = {
        'wins': singles_wins + tag_wins,
        'losses': singles_losses + tag_losses,
        'draws': singles_draws + tag_draws
    }

    return render_template('fan/wrestler.html', wrestler=wrestler, prefs=prefs, total_record=total_record)

@fan_bp.route('/tagteam/<string:tagteam_name>')
def view_tagteam(tagteam_name):
    """Renders the fan view page for a specific tag team."""
    prefs = load_preferences()
    tagteam = get_tagteam_by_name(tagteam_name)

    if not tagteam:
        flash(f"Tag Team '{tagteam_name}' not found.", 'danger')
        return redirect(url_for('fan.roster'))

    return render_template('fan/tagteam.html', tagteam=tagteam, prefs=prefs)

@fan_bp.route('/event/<string:event_slug>')
def view_event(event_slug):
    """Renders the fan view page for a specific event."""
    prefs = load_preferences()
    event = get_event_by_slug(event_slug) # Use the new function to find by slug

    if not event:
        flash(f"Event '{event_slug}' not found.", 'danger')
        return redirect(url_for('fan.home')) # Redirect to fan home if event not found

    segments = load_segments(_slugify(event_slug))
    segments.sort(key=lambda s: s.get('position', 9999)) # Sort segments by position

    # Iterate through segments to merge match visibility data
    for segment in segments:
        if segment.get('type') == 'Match' and segment.get('match_id'):
            match_data = get_match_by_id(_slugify(event_slug), segment['match_id'])
            if match_data and 'match_visibility' in match_data:
                # Merge visibility flags into the segment dictionary
                segment['on_card'] = not match_data['match_visibility'].get('hide_from_card', False)
                segment['include_in_results'] = not match_data['match_visibility'].get('hide_result', False)
                # Note: hide_summary is handled in the finalize_event process, not directly here for display logic
            else:
                # Default to visible if match data or visibility info is missing
                segment['on_card'] = True
                segment['include_in_results'] = True
        else:
            # Non-match segments are always considered "on card" and "in results" for display purposes
            segment['on_card'] = True
            segment['include_in_results'] = True

    event_summary_content = load_event_summary_content(event.get('event_summary_file'))

    return render_template(
        'fan/event.html',
        event=event,
        segments=segments,
        prefs=prefs,
        event_summary_content=event_summary_content
    )

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
    # Sort divisions by Display_Position for consistent display
    sorted_divisions = sorted(all_divisions, key=lambda d: d.get('Display_Position', 0))
    
    roster_by_division = {}
    for division in sorted_divisions:
        division_id = division.get('ID')
        division_name = division.get('Name')
        # Store the division type as well for template logic
        roster_by_division[division_name] = {'wrestlers': [], 'tagteams': [], 'type': division.get('Holder_Type')}

        # Add wrestlers to their division
        for wrestler in active_wrestlers:
            if wrestler.get('Division') == division_id:
                roster_by_division[division_name]['wrestlers'].append(wrestler)
        
        # Add tag teams to their division
        for tagteam in active_tagteams:
            if tagteam.get('Division') == division_id:
                roster_by_division[division_name]['tagteams'].append(tagteam)

    # Filter out divisions that have no active wrestlers or tagteams
    # This needs to be done after sorting and grouping
    filtered_roster_by_division = {
        div_name: data for div_name, data in roster_by_division.items()
        if data['wrestlers'] or data['tagteams']
    }

    # Sorting logic
    sort_order = prefs.get('fan_mode_roster_sort_order', 'Alphabetical')

    # Apply sorting to the filtered data
    for division_name, data in filtered_roster_by_division.items():
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

    return render_template('fan/roster.html', roster_data=filtered_roster_by_division, prefs=prefs)
