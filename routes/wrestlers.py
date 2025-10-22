from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.wrestlers import load_wrestlers, get_wrestler_by_name, add_wrestler, update_wrestler, delete_wrestler
from src import divisions
import html

wrestlers_bp = Blueprint('wrestlers', __name__, url_prefix='/wrestlers')

STATUS_OPTIONS = ['Active', 'Inactive', 'Injured']
ALIGNMENT_OPTIONS = ['Hero', 'Babyface', 'Anti-hero', 'Tweener', 'Heel', 'Villain']
WRESTLING_STYLES_OPTIONS = ["All-Rounder", "Brawler", "Dirty", "High-Flyer", "Luchador", "Powerhouse", "Striker", "Submission Specialist", "Technical"]

def is_wrestler_deletable(wrestler):
    return all(int(wrestler.get(key, 0)) == 0 for key in ['Singles_Wins', 'Singles_Losses', 'Singles_Draws', 'Tag_Wins', 'Tag_Losses', 'Tag_Draws'])

def _get_form_data(form):
    return {
        "Name": html.escape(form['name'].strip()),
        "Status": html.escape(form['status'].strip()), "Division": html.escape(form['division'].strip()),
        "Nickname": html.escape(form.get('nickname', '').strip()), "Location": html.escape(form.get('location', '').strip()),
        "Height": html.escape(form.get('height', '').strip()), "Weight": html.escape(form.get('weight', '').strip()),
        "DOB": html.escape(form.get('dob', '').strip()), "Alignment": html.escape(form['alignment'].strip()),
        "Music": html.escape(form.get('music', '').strip()),
        "Faction": html.escape(form.get('faction', '').strip()), "Manager": html.escape(form.get('manager', '').strip()),
        "Moves": html.escape(form.get('moves', '').strip()).replace('\n', '|').replace('\r', ''),
        "Awards": html.escape(form.get('awards', '').strip()).replace('\n', '|').replace('\r', ''),
        "Real_Name": html.escape(form.get('real_name', '').strip()), "Start_Date": html.escape(form.get('start_date', '').strip()),
        "Salary": html.escape(form.get('salary', '').strip()).replace('\n', '|').replace('\r', ''),
        "Wrestling_Styles": '|'.join(html.escape(s.strip()) for s in form.getlist('wrestling_styles')),
        "Hide_From_Fan_Roster": 'hide_from_fan_roster' in form
    }

@wrestlers_bp.route('/')
def list_wrestlers():
    selected_status = request.args.get('status', 'All')
    all_wrestlers = sorted(load_wrestlers(), key=lambda w: w.get('Name', ''))

    if selected_status != 'All':
        wrestlers_list = [w for w in all_wrestlers if w.get('Status') == selected_status]
    else:
        wrestlers_list = all_wrestlers

    for wrestler in wrestlers_list:
        wrestler['DivisionName'] = divisions.get_division_name_by_id(wrestler.get('Division', ''))
        wrestler['is_deletable'] = is_wrestler_deletable(wrestler)

    status_options_for_filter = ['All'] + STATUS_OPTIONS
    return render_template('booker/wrestlers/list.html',
                           wrestlers=wrestlers_list,
                           status_options=status_options_for_filter,
                           selected_status=selected_status)

@wrestlers_bp.route('/create', methods=['GET', 'POST'])
def create_wrestler():
    all_divisions = divisions.get_all_division_ids_and_names()
    if request.method == 'POST':
        wrestler_data = _get_form_data(request.form)
        wrestler_data['Team'] = '' # Initialize read-only fields
        wrestler_data['Belt'] = ''
        wrestler_data.update({'Singles_Wins': '0', 'Singles_Losses': '0', 'Singles_Draws': '0', 'Tag_Wins': '0', 'Tag_Losses': '0', 'Tag_Draws': '0'})
        
        if not wrestler_data.get('Name'): flash('Wrestler Name is required.', 'error')
        elif add_wrestler(wrestler_data):
            flash(f'Wrestler "{wrestler_data["Name"]}" created successfully!', 'success')
            return redirect(url_for('wrestlers.list_wrestlers'))
        else: flash(f'Wrestler with the name "{wrestler_data["Name"]}" already exists.', 'error')
        return render_template('booker/wrestlers/form.html', wrestler=wrestler_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, wrestling_styles_options=WRESTLING_STYLES_OPTIONS, edit_mode=False)
    return render_template('booker/wrestlers/form.html', wrestler={}, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, wrestling_styles_options=WRESTLING_STYLES_OPTIONS, edit_mode=False)

@wrestlers_bp.route('/edit/<string:wrestler_name>', methods=['GET', 'POST'])
def edit_wrestler(wrestler_name):
    wrestler = get_wrestler_by_name(wrestler_name)
    if not wrestler:
        flash(f'Wrestler "{wrestler_name}" not found.', 'error')
        return redirect(url_for('wrestlers.list_wrestlers'))
    all_divisions = divisions.get_all_division_ids_and_names()
    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        # Preserve read-only fields from the original data
        for key in ['Team', 'Belt', 'Singles_Wins', 'Singles_Losses', 'Singles_Draws', 'Tag_Wins', 'Tag_Losses', 'Tag_Draws']:
            updated_data[key] = wrestler.get(key, '0')

        if not updated_data.get('Name'): flash('Wrestler Name is required.', 'error')
        elif update_wrestler(wrestler_name, updated_data):
            flash(f'Wrestler "{updated_data["Name"]}" updated successfully!', 'success')
            return redirect(url_for('wrestlers.list_wrestlers'))
        else: flash(f'Failed to update wrestler "{wrestler_name}". New name might already exist.', 'error')
        return render_template('booker/wrestlers/form.html', wrestler=updated_data, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, wrestling_styles_options=WRESTLING_STYLES_OPTIONS, edit_mode=True)

    wrestler_display = wrestler.copy()
    wrestler_display['Moves'] = wrestler_display.get('Moves', '').replace('|', '\n')
    wrestler_display['Awards'] = wrestler_display.get('Awards', '').replace('|', '\n')
    wrestler_display['Salary'] = wrestler_display.get('Salary', '').replace('|', '\n')
    # Convert pipe-delimited string back to a list for checkbox checking
    wrestler_display['Wrestling_Styles'] = wrestler_display.get('Wrestling_Styles', '').split('|') if wrestler_display.get('Wrestling_Styles') else []
    return render_template('booker/wrestlers/form.html', wrestler=wrestler_display, status_options=STATUS_OPTIONS, alignment_options=ALIGNMENT_OPTIONS, divisions=all_divisions, wrestling_styles_options=WRESTLING_STYLES_OPTIONS, edit_mode=True)

@wrestlers_bp.route('/view/<string:wrestler_name>')
def view_wrestler(wrestler_name):
    wrestler = get_wrestler_by_name(wrestler_name)
    if not wrestler:
        flash(f'Wrestler "{wrestler_name}" not found.', 'error')
        return redirect(url_for('wrestlers.list_wrestlers'))
    wrestler['DivisionName'] = divisions.get_division_name_by_id(wrestler.get('Division', ''))
    return render_template('booker/wrestlers/view.html', wrestler=wrestler)

@wrestlers_bp.route('/delete/<string:wrestler_name>', methods=['POST'])
def delete_wrestler_route(wrestler_name):
    wrestler = get_wrestler_by_name(wrestler_name)
    if wrestler and not is_wrestler_deletable(wrestler):
        flash('Cannot delete a wrestler who has a match record.', 'danger')
        return redirect(url_for('wrestlers.list_wrestlers'))
    if delete_wrestler(wrestler_name):
        flash(f'Wrestler "{wrestler_name}" deleted successfully!', 'success')
    else:
        flash(f'Failed to delete wrestler "{wrestler_name}".', 'error')
    return redirect(url_for('wrestlers.list_wrestlers'))

