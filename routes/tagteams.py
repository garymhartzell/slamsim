from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.tagteams import (
    load_tagteams, save_tagteams, get_tagteam_by_name,
    add_tagteam, update_tagteam, delete_tagteam,
    get_wrestler_names, get_active_members_status
)
from werkzeug.utils import escape

tagteams_bp = Blueprint('tagteams', __name__, url_prefix='/tagteams')

STATUS_OPTIONS = ['Active', 'Inactive']
ALIGNMENT_OPTIONS = ['Babyface', 'Tweener', 'Heel']

def _get_form_data(form):
    """Extracts and processes tag-team data from the form."""
    member_names = [form.get('Member1'), form.get('Member2')]
    if form.get('Member3'):
        member_names.append(form.get('Member3'))
    
    # Filter out empty member names before joining
    members_string = '|'.join(filter(None, member_names))

    # Determine status based on members' activity
    member_status_active = get_active_members_status(filter(None, member_names))
    tagteam_status = form.get('Status')
    if tagteam_status == 'Active' and not member_status_active:
        flash("Cannot set tag-team status to 'Active' because one or more members are inactive.", 'warning')
        tagteam_status = 'Inactive' # Force inactive if members are not active

    return {
        "Name": escape(form.get('Name', '')).strip(),
        "Wins": escape(form.get('Wins', '0')).strip(),
        "Losses": escape(form.get('Losses', '0')).strip(),
        "Draws": escape(form.get('Draws', '0')).strip(),
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
        "Belt": escape(form.get('Belt', '')).strip(),
        "Awards": escape(form.get('Awards', '')).strip()
    }

@tagteams_bp.route('/')
def list_tagteams():
    """Displays a list of all tag-teams."""
    tagteams = load_tagteams()
    return render_template('tagteams/list.html', tagteams=tagteams)

@tagteams_bp.route('/create', methods=['GET', 'POST'])
def create_tagteam():
    """Handles creation of a new tag-team."""
    wrestler_names = get_wrestler_names()
    if request.method == 'POST':
        tagteam_data = _get_form_data(request.form)
        
        # Basic validation
        if not tagteam_data['Name']:
            flash('Tag-team Name is required.', 'danger')
            return render_template('tagteams/form.html', tagteam={}, 
                                   status_options=STATUS_OPTIONS,
                                   alignment_options=ALIGNMENT_OPTIONS,
                                   wrestler_names=wrestler_names,
                                   edit_mode=False)
        
        if not request.form.get('Member1') or not request.form.get('Member2'):
            flash('At least two members are required for a tag-team.', 'danger')
            return render_template('tagteams/form.html', tagteam=tagteam_data, 
                                   status_options=STATUS_OPTIONS,
                                   alignment_options=ALIGNMENT_OPTIONS,
                                   wrestler_names=wrestler_names,
                                   edit_mode=False)

        # Check for duplicate name
        if get_tagteam_by_name(tagteam_data['Name']):
            flash(f"A tag-team with the name '{tagteam_data['Name']}' already exists.", 'danger')
            return render_template('tagteams/form.html', tagteam=tagteam_data, 
                                   status_options=STATUS_OPTIONS,
                                   alignment_options=ALIGNMENT_OPTIONS,
                                   wrestler_names=wrestler_names,
                                   edit_mode=False)
        
        add_tagteam(tagteam_data)
        flash(f"Tag-team '{tagteam_data['Name']}' created successfully!", 'success')
        return redirect(url_for('tagteams.list_tagteams'))
    
    return render_template('tagteams/form.html', tagteam={}, 
                           status_options=STATUS_OPTIONS,
                           alignment_options=ALIGNMENT_OPTIONS,
                           wrestler_names=wrestler_names,
                           edit_mode=False)

@tagteams_bp.route('/edit/<string:tagteam_name>', methods=['GET', 'POST'])
def edit_tagteam(tagteam_name):
    """Handles editing of an existing tag-team."""
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))

    wrestler_names = get_wrestler_names()

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)

        if not updated_data['Name']:
            flash('Tag-team Name is required.', 'danger')
            return render_template('tagteams/form.html', tagteam=tagteam, 
                                   status_options=STATUS_OPTIONS,
                                   alignment_options=ALIGNMENT_OPTIONS,
                                   wrestler_names=wrestler_names,
                                   edit_mode=True)
        
        if not request.form.get('Member1') or not request.form.get('Member2'):
            flash('At least two members are required for a tag-team.', 'danger')
            return render_template('tagteams/form.html', tagteam=updated_data, 
                                   status_options=STATUS_OPTIONS,
                                   alignment_options=ALIGNMENT_OPTIONS,
                                   wrestler_names=wrestler_names,
                                   edit_mode=True)

        # Check for duplicate name only if the name has changed
        if updated_data['Name'] != tagteam_name and get_tagteam_by_name(updated_data['Name']):
            flash(f"A tag-team with the name '{updated_data['Name']}' already exists.", 'danger')
            return render_template('tagteams/form.html', tagteam=updated_data, 
                                   status_options=STATUS_OPTIONS,
                                   alignment_options=ALIGNMENT_OPTIONS,
                                   wrestler_names=wrestler_names,
                                   edit_mode=True)

        update_tagteam(tagteam_name, updated_data)
        flash(f"Tag-team '{updated_data['Name']}' updated successfully!", 'success')
        return redirect(url_for('tagteams.list_tagteams'))
    
    # Pre-fill form for GET request
    # Split members string back into individual fields for dropdowns
    members_list = tagteam.get('Members', '').split('|')
    tagteam['Member1'] = members_list[0] if len(members_list) > 0 else ''
    tagteam['Member2'] = members_list[1] if len(members_list) > 1 else ''
    tagteam['Member3'] = members_list[2] if len(members_list) > 2 else ''

    return render_template('tagteams/form.html', tagteam=tagteam, 
                           status_options=STATUS_OPTIONS,
                           alignment_options=ALIGNMENT_OPTIONS,
                           wrestler_names=wrestler_names,
                           edit_mode=True)

@tagteams_bp.route('/view/<string:tagteam_name>')
def view_tagteam(tagteam_name):
    """Displays details of a single tag-team."""
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))
    
    # Split members, moves, and awards for display
    tagteam['Members'] = tagteam.get('Members', '').split('|')
    tagteam['Moves'] = tagteam.get('Moves', '').split('|')
    tagteam['Awards'] = tagteam.get('Awards', '').split('|')

    return render_template('tagteams/view.html', tagteam=tagteam)

@tagteams_bp.route('/delete/<string:tagteam_name>', methods=['POST'])
def delete_tagteam_route(tagteam_name):
    """Handles deletion of a tag-team."""
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
    else:
        delete_tagteam(tagteam_name)
        flash(f"Tag-team '{tagteam_name}' deleted successfully!", 'success')
    return redirect(url_for('tagteams.list_tagteams'))
