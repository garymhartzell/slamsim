from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.tagteams import (
    load_tagteams, get_tagteam_by_name,
    add_tagteam, update_tagteam, delete_tagteam,
    get_wrestler_names, get_active_members_status
)
from src import divisions
from werkzeug.utils import escape

tagteams_bp = Blueprint('tagteams', __name__, url_prefix='/tagteams')

STATUS_OPTIONS = ['Active', 'Inactive']
ALIGNMENT_OPTIONS = ['Babyface', 'Tweener', 'Heel']

def _get_form_data(form):
    """Extracts and processes tag-team data from the form."""
    member_names = [form.get('Member1'), form.get('Member2'), form.get('Member3')]
    members_string = '|'.join(filter(None, member_names))
    member_status_active = get_active_members_status(filter(None, member_names))
    tagteam_status = form.get('Status')
    if tagteam_status == 'Active' and not member_status_active:
        flash("Cannot set to 'Active' because one or more members are inactive.", 'warning')
        tagteam_status = 'Inactive'

    data = {
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
        "Awards": escape(form.get('Awards', '')).strip()
    }
    # Preserve existing belt value since it's removed from the form
    if 'Name' in form:
        existing_team = get_tagteam_by_name(form['Name'])
        if existing_team:
            data['Belt'] = existing_team.get('Belt', '')
    return data

@tagteams_bp.route('/')
def list_tagteams():
    tagteams_list = load_tagteams()
    for team in tagteams_list:
        team['DivisionName'] = divisions.get_division_name_by_id(team.get('Division', ''))
    return render_template('tagteams/list.html', tagteams=tagteams_list)

@tagteams_bp.route('/create', methods=['GET', 'POST'])
def create_tagteam():
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
            flash(f"Tag-team '{tagteam_data['Name']}' created successfully!", 'success')
            return redirect(url_for('tagteams.list_tagteams'))
        return render_template('tagteams/form.html', tagteam=tagteam_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=False)
    return render_template('tagteams/form.html', tagteam={}, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=False)

@tagteams_bp.route('/edit/<string:tagteam_name>', methods=['GET', 'POST'])
def edit_tagteam(tagteam_name):
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))
    wrestler_names = get_wrestler_names()
    all_divisions = divisions.get_all_division_ids_and_names()
    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        updated_data['Belt'] = tagteam.get('Belt', '') # Preserve existing belt
        if not updated_data['Name']:
            flash('Tag-team Name is required.', 'danger')
        elif not request.form.get('Member1') or not request.form.get('Member2'):
            flash('At least two members are required.', 'danger')
        elif updated_data['Name'] != tagteam_name and get_tagteam_by_name(updated_data['Name']):
            flash(f"A tag-team with the name '{updated_data['Name']}' already exists.", 'danger')
        else:
            update_tagteam(tagteam_name, updated_data)
            flash(f"Tag-team '{updated_data['Name']}' updated successfully!", 'success')
            return redirect(url_for('tagteams.list_tagteams'))
        return render_template('tagteams/form.html', tagteam=updated_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=True)
    
    members_list = tagteam.get('Members', '').split('|')
    tagteam['Member1'] = members_list[0] if len(members_list) > 0 else ''
    tagteam['Member2'] = members_list[1] if len(members_list) > 1 else ''
    tagteam['Member3'] = members_list[2] if len(members_list) > 2 else ''
    return render_template('tagteams/form.html', tagteam=tagteam, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, wrestler_names=wrestler_names, divisions=all_divisions, edit_mode=True)

@tagteams_bp.route('/view/<string:tagteam_name>')
def view_tagteam(tagteam_name):
    tagteam = get_tagteam_by_name(tagteam_name)
    if not tagteam:
        flash('Tag-team not found!', 'danger')
        return redirect(url_for('tagteams.list_tagteams'))
    tagteam['DivisionName'] = divisions.get_division_name_by_id(tagteam.get('Division', ''))
    return render_template('tagteams/view.html', tagteam=tagteam)

@tagteams_bp.route('/delete/<string:tagteam_name>', methods=['POST'])
def delete_tagteam_route(tagteam_name):
    delete_tagteam(tagteam_name)
    flash(f"Tag-team '{tagteam_name}' deleted successfully!", 'success')
    return redirect(url_for('tagteams.list_tagteams'))

