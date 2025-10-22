from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.tagteams import (
    load_tagteams, get_tagteam_by_name, add_tagteam, update_tagteam, 
    delete_tagteam, get_wrestler_names, get_active_members_status
)
from src.wrestlers import update_wrestler_team_affiliation
from src import divisions
from werkzeug.utils import escape

tagteams_bp = Blueprint('tagteams', __name__, url_prefix='/tagteams')

def _sort_key_ignore_the(name):
    """Returns a sort key that ignores a leading 'The '."""
    if name.lower().startswith('the '):
        return name[4:]
    return name

STATUS_OPTIONS = ['Active', 'Inactive']
ALIGNMENT_OPTIONS = ['Babyface', 'Tweener', 'Heel']

def is_tagteam_deletable(team):
    """Check if a tag team has a non-zero record."""
    return all(int(team.get(key, 0)) == 0 for key in ['Wins', 'Losses', 'Draws'])

def _get_form_data(form):
    """Extracts and processes tag-team data from the form."""
    member_names = [form.get('Member1'), form.get('Member2'), form.get('Member3')]
    members_string = '|'.join(filter(None, member_names))

    member_status_active = get_active_members_status(filter(None, member_names))
    tagteam_status = form.get('Status')
    if tagteam_status == 'Active' and not member_status_active:
        flash("Cannot set tag-team status to 'Active' because one or more members are inactive.", 'warning')
        tagteam_status = 'Inactive'

    return {
        "Name": escape(form.get('Name', '')).strip(),
        "Wins": escape(form.get('Wins', '0')),
        "Losses": escape(form.get('Losses', '0')),
        "Draws": escape(form.get('Draws', '0')),
        "Status": tagteam_status,
        "Division": escape(form.get('Division', '')).strip(),
        "Location": escape(form.get('Location', '')).strip(),
        "Weight": escape(form.get('Weight', '')).strip(),
        "Alignment": form.get('Alignment', ''),
        "Music": escape(form.get('Music', '')).strip(),
        "Members": members_string,
        "Faction": escape(form.get('Faction', '')).strip(),
        "Manager": escape(form.get('Manager', '')).strip(),
        "Moves": escape(form.get('Moves', '')).strip(),
        "Awards": escape(form.get('Awards', '')).strip(),
        "Hide_From_Fan_Roster": 'hide_from_fan_roster' in form
    }

@tagteams_bp.route('/')
def list_tagteams():
    """Displays a list of all tag-teams, sorted alphabetically, with deletable check."""
    selected_status = request.args.get('status', 'All')
    all_tagteams = sorted(load_tagteams(), key=lambda t: _sort_key_ignore_the(t.get('Name', '')))

    if selected_status != 'All':
        tagteams_list = [t for t in all_tagteams if t.get('Status') == selected_status]
    else:
        tagteams_list = all_tagteams

    for team in tagteams_list:
        team['DivisionName'] = divisions.get_division_name_by_id(team.get('Division', ''))
        team['is_deletable'] = is_tagteam_deletable(team)

    status_options_for_filter = ['All'] + STATUS_OPTIONS
    return render_template('booker/tagteams/list.html',
                           tagteams=tagteams_list,
                           status_options=status_options_for_filter,
                           selected_status=selected_status)

@tagteams_bp.route('/create', methods=['GET', 'POST'])
def create_tagteam():
    """Handles creation of a new tag-team."""
    wrestler_names = get_wrestler_names()
    all_divisions = divisions.get_all_division_ids_and_names()
    if request.method == 'POST':
        tagteam_data = _get_form_data(request.form)
        tagteam_data['Belt'] = '' # New teams don't have belts
        if not tagteam_data['Name']:
            flash('Tag-team Name is required.', 'danger')
        elif not request.form.get('Member1') or not request.form.get('Member2'):
            flash('At least two members are required.', 'danger')
        elif get_tagteam_by_name(tagteam_data['Name']):
            flash(f"A tag-team with the name '{tagteam_data['Name']}' already exists.", 'danger')
        else:
            add_tagteam(tagteam_data)
            # Sync wrestler team fields
            for member_name in tagteam_data.get('Members', '').split('|'):
                if member_name: update_wrestler_team_affiliation(member_name, tagteam_data['Name'])
            flash(f"Tag-team '{tagteam_data['Name']}' created successfully!", 'success')
            return redirect(url_for('tagteams.list_tagteams'))
        return render_template('booker/tagteams/form.html', tagteam=tagteam_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=False)
    return render_template('booker/tagteams/form.html', tagteam={}, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=False)

@tagteams_bp.route('/edit/<string:tagteam_name>', methods=['GET', 'POST'])
def edit_tagteam(tagteam_name):
    """Handles editing of an existing tag-team."""
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))
    
    wrestler_names = get_wrestler_names()
    all_divisions = divisions.get_all_division_ids_and_names()
    old_members = set(tagteam.get('Members', '').split('|')) if tagteam else set()

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        updated_data['Belt'] = tagteam.get('Belt', '') # Preserve existing belt value
        
        if not updated_data['Name']:
            flash('Tag-team Name is required.', 'danger')
        elif not request.form.get('Member1') or not request.form.get('Member2'):
            flash('At least two members are required.', 'danger')
        elif updated_data['Name'] != tagteam_name and get_tagteam_by_name(updated_data['Name']):
            flash(f"A tag-team with the name '{updated_data['Name']}' already exists.", 'danger')
        else:
            update_tagteam(tagteam_name, updated_data)
            
            # Sync wrestler team fields
            new_members = set(updated_data.get('Members', '').split('|'))
            removed_members = old_members - new_members
            added_members = new_members - old_members
            name_changed = updated_data['Name'] != tagteam_name

            for member in removed_members:
                if member: update_wrestler_team_affiliation(member, '') # Clear team
            for member in added_members:
                if member: update_wrestler_team_affiliation(member, updated_data['Name'])
            if name_changed: # If team name changed, update all current members
                for member in new_members:
                    if member: update_wrestler_team_affiliation(member, updated_data['Name'])

            flash(f"Tag-team '{updated_data['Name']}' updated successfully!", 'success')
            return redirect(url_for('tagteams.list_tagteams'))
        return render_template('booker/tagteams/form.html', tagteam=updated_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=True)
    
    # Pre-fill form for GET request
    members_list = tagteam.get('Members', '').split('|')
    tagteam['Member1'] = members_list[0] if len(members_list) > 0 else ''
    tagteam['Member2'] = members_list[1] if len(members_list) > 1 else ''
    tagteam['Member3'] = members_list[2] if len(members_list) > 2 else ''
    return render_template('booker/tagteams/form.html', tagteam=tagteam, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=True)

@tagteams_bp.route('/view/<string:tagteam_name>')
def view_tagteam(tagteam_name):
    """Displays details of a single tag-team."""
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))
    tagteam['DivisionName'] = divisions.get_division_name_by_id(tagteam.get('Division', ''))
    return render_template('booker/tagteams/view.html', tagteam=tagteam)

@tagteams_bp.route('/delete/<string:tagteam_name>', methods=['POST'])
def delete_tagteam_route(tagteam_name):
    """Handles deletion of a tag-team."""
    team = get_tagteam_by_name(tagteam_name)
    if team and not is_tagteam_deletable(team):
        flash('Cannot delete a tag team that has a match record.', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))

    # Clear team affiliation from members before deleting
    if team and team.get('Members'):
        for member_name in team['Members'].split('|'):
            if member_name: update_wrestler_team_affiliation(member_name, '')
            
    delete_tagteam(tagteam_name)
    flash(f"Tag-team '{tagteam_name}' deleted successfully!", 'success')
    return redirect(url_for('tagteams.list_tagteams'))

