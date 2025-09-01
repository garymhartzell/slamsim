from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.wrestlers import load_wrestlers, get_wrestler_by_name, add_wrestler, update_wrestler, delete_wrestler
from src import divisions # Import divisions
import html # Import the html module for sanitization

wrestlers_bp = Blueprint('wrestlers', __name__, url_prefix='/wrestlers')

# Dropdown options for Status and Alignment
STATUS_OPTIONS = ['Active', 'Inactive', 'Injured']
ALIGNMENT_OPTIONS = ['Hero', 'Babyface', 'Anti-hero', 'Tweener', 'Heel', 'Villain']

def _get_form_data(form):
    """Helper to extract, sanitize, and format form data."""
    data = {
        "Name": html.escape(form['name'].strip()),
        "Singles_Wins": html.escape(form['singles_wins'].strip()),
        "Singles_Losses": html.escape(form['singles_losses'].strip()),
        "Singles_Draws": html.escape(form['singles_draws'].strip()),
        "Tag_Wins": html.escape(form['tag_wins'].strip()),
        "Tag_Losses": html.escape(form['tag_losses'].strip()),
        "Tag_Draws": html.escape(form['tag_draws'].strip()),
        "Status": html.escape(form['status'].strip()),
        "Division": html.escape(form['division'].strip()),
        "Nickname": html.escape(form['nickname'].strip()),
        "Location": html.escape(form['location'].strip()),
        "Height": html.escape(form['height'].strip()),
        "Weight": html.escape(form['weight'].strip()),
        "DOB": html.escape(form['dob'].strip()),
        "Alignment": html.escape(form['alignment'].strip()),
        "Music": html.escape(form['music'].strip()),
        "Team": html.escape(form['team'].strip()),
        "Faction": html.escape(form['faction'].strip()),
        "Manager": html.escape(form['manager'].strip()),
        "Moves": html.escape(form['moves'].strip()).replace('\n', '|').replace('\r', ''),
        "Belt": html.escape(form['belt'].strip()),
        "Awards": html.escape(form['awards'].strip()).replace('\n', '|').replace('\r', ''), # displayed as Accomplishments
        "Real_Name": html.escape(form['real_name'].strip()),
        "Start_Date": html.escape(form['start_date'].strip()),
        "Salary": html.escape(form['salary'].strip()).replace('\n', '|').replace('\r', '')
    }
    return data

@wrestlers_bp.route('/')
def list_wrestlers():
    """Displays a list of all wrestlers."""
    wrestlers_list = load_wrestlers()
    for wrestler in wrestlers_list:
        wrestler['DivisionName'] = divisions.get_division_name_by_id(wrestler.get('Division', ''))
    return render_template('wrestlers/list.html', wrestlers=wrestlers_list)

@wrestlers_bp.route('/create', methods=['GET', 'POST'])
def create_wrestler():
    """Handles creation of a new wrestler."""
    all_divisions = divisions.get_all_division_ids_and_names()
    if request.method == 'POST':
        wrestler_data = _get_form_data(request.form)
        if not wrestler_data.get('Name'):
            flash('Wrestler Name is required.', 'error')
            return render_template('wrestlers/form.html', wrestler={}, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=False)
        
        if wrestler_data.get('Division') not in [d['ID'] for d in all_divisions]:
            flash('Invalid Division selected.', 'error')
            return render_template('wrestlers/form.html', wrestler=wrestler_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=False)

        if add_wrestler(wrestler_data):
            flash(f'Wrestler "{wrestler_data["Name"]}" created successfully!', 'success')
            return redirect(url_for('wrestlers.list_wrestlers'))
        else:
            flash(f'Wrestler with the name "{wrestler_data["Name"]}" already exists. Please choose a unique name.', 'error')
    
    # GET request or failed POST
    return render_template('wrestlers/form.html', wrestler={}, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=False)

@wrestlers_bp.route('/edit/<string:wrestler_name>', methods=['GET', 'POST'])
def edit_wrestler(wrestler_name):
    """Handles editing an existing wrestler."""
    wrestler = get_wrestler_by_name(wrestler_name)
    if not wrestler:
        flash(f'Wrestler "{wrestler_name}" not found.', 'error')
        return redirect(url_for('wrestlers.list_wrestlers'))

    all_divisions = divisions.get_all_division_ids_and_names()

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        if not updated_data.get('Name'):
            flash('Wrestler Name is required.', 'error')
            # Retain current wrestler data on error for user convenience
            return render_template('wrestlers/form.html', wrestler=wrestler, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=True)
        
        if updated_data.get('Division') not in [d['ID'] for d in all_divisions]:
            flash('Invalid Division selected.', 'error')
            return render_template('wrestlers/form.html', wrestler=updated_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=True)

        # The wrestler_name might have been changed in the form, so pass the original name for lookup
        if update_wrestler(wrestler_name, updated_data):
            flash(f'Wrestler "{updated_data["Name"]}" updated successfully!', 'success')
            return redirect(url_for('wrestlers.list_wrestlers'))
        else:
            flash(f'Failed to update wrestler "{wrestler_name}". A wrestler with the new name "{updated_data["Name"]}" might already exist, or the wrestler was not found.', 'error')
            # If update failed (e.g., name conflict), re-render with the data the user tried to submit
            updated_data_display = updated_data.copy()
            if 'Moves' in updated_data_display and updated_data_display['Moves']:
                updated_data_display['Moves'] = updated_data_display['Moves'].replace('|', '\n')
            if 'Awards' in updated_data_display and updated_data_display['Awards']:
                updated_data_display['Awards'] = updated_data_display['Awards'].replace('|', '\n')
            if 'Salary' in updated_data_display and updated_data_display['Salary']:
                updated_data_display['Salary'] = updated_data_display['Salary'].replace('|', '\n')
            return render_template('wrestlers/form.html', wrestler=updated_data_display, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=True)

    # GET request
    # Format multiline fields for textarea display
    wrestler_display = wrestler.copy()
    if 'Moves' in wrestler_display and wrestler_display['Moves']:
        wrestler_display['Moves'] = wrestler_display['Moves'].replace('|', '\n')
    if 'Awards' in wrestler_display and wrestler_display['Awards']:
        wrestler_display['Awards'] = wrestler_display['Awards'].replace('|', '\n')
    if 'Salary' in wrestler_display and wrestler_display['Salary']:
        wrestler_display['Salary'] = wrestler_display['Salary'].replace('|', '\n')

    return render_template('wrestlers/form.html', wrestler=wrestler_display, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, edit_mode=True)

@wrestlers_bp.route('/view/<string:wrestler_name>')
def view_wrestler(wrestler_name):
    """Displays details of a single wrestler."""
    wrestler = get_wrestler_by_name(wrestler_name)
    if not wrestler:
        flash(f'Wrestler "{wrestler_name}" not found.', 'error')
        return redirect(url_for('wrestlers.list_wrestlers'))
    
    wrestler['DivisionName'] = divisions.get_division_name_by_id(wrestler.get('Division', ''))
    return render_template('wrestlers/view.html', wrestler=wrestler)

@wrestlers_bp.route('/delete/<string:wrestler_name>', methods=['POST'])
def delete_wrestler_route(wrestler_name):
    """Handles deletion of a wrestler."""
    if delete_wrestler(wrestler_name):
        flash(f'Wrestler "{wrestler_name}" deleted successfully!', 'success')
    else:
        flash(f'Failed to delete wrestler "{wrestler_name}". Wrestler not found.', 'error')
    return redirect(url_for('wrestlers.list_wrestlers'))
