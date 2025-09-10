from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.belts import (
    load_belts, add_belt, get_belt_by_id, update_belt, delete_belt,
    load_history_for_belt, add_reign_to_history, get_reign_by_id,
    update_reign_in_history, delete_reign_from_history
)
from src.wrestlers import load_wrestlers
from src.tagteams import load_tagteams
from src.segments import _slugify
import uuid
from datetime import datetime

belts_bp = Blueprint('belts', __name__, url_prefix='/belts')

STATUS_OPTIONS = ['Active', 'Vacant']
HOLDER_TYPE_OPTIONS = ['Singles', 'Tag-Team']

def _get_form_data(form, is_create=False):
    data = {
        'Name': form.get('name', '').strip(), 'Status': form.get('status', '').strip(),
        'Holder_Type': form.get('holder_type', '').strip(), 'Current_Holder': form.get('current_holder', '').strip()
    }
    if is_create:
        base_id = _slugify(data['Name'])
        unique_suffix = str(uuid.uuid4())[:4]
        data['ID'] = f"{base_id}-{unique_suffix}"
    else: data['ID'] = form.get('belt_id', '').strip()
    return data

@belts_bp.route('/')
def list_belts():
    all_belts = load_belts()
    for belt in all_belts:
        belt['is_deletable'] = not bool(load_history_for_belt(belt['ID']))
    return render_template('belts/list.html', belts=all_belts)

@belts_bp.route('/create', methods=['GET', 'POST'])
def create_belt():
    wrestlers = sorted([w['Name'] for w in load_wrestlers()])
    tagteams = sorted([t['Name'] for t in load_tagteams()])
    if request.method == 'POST':
        belt_data = _get_form_data(request.form, is_create=True)
        if not all([belt_data['Name'], belt_data['Status'], belt_data['Holder_Type']]):
            flash('Name, Status, and Holder Type are required.', 'danger')
        else:
            success, message = add_belt(belt_data)
            if success:
                flash(message, 'success')
                return redirect(url_for('belts.list_belts'))
            else: flash(message, 'danger')
        return render_template('belts/form.html', belt=belt_data, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='create')
    return render_template('belts/form.html', belt={}, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='create')

@belts_bp.route('/edit/<string:belt_id>', methods=['GET', 'POST'])
def edit_belt(belt_id):
    belt_to_edit = get_belt_by_id(belt_id)
    if not belt_to_edit:
        flash('Belt not found.', 'danger')
        return redirect(url_for('belts.list_belts'))
    wrestlers = sorted([w['Name'] for w in load_wrestlers()])
    tagteams = sorted([t['Name'] for t in load_tagteams()])
    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        if updated_data['ID'] != belt_id:
            flash('Belt ID cannot be changed.', 'danger')
        else:
            success, message = update_belt(belt_id, updated_data)
            if success:
                flash(message, 'success')
                return redirect(url_for('belts.list_belts'))
            else: flash(message, 'danger')
        return render_template('belts/form.html', belt=updated_data, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='edit')
    return render_template('belts/form.html', belt=belt_to_edit, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='edit')

@belts_bp.route('/delete/<string:belt_id>', methods=['POST'])
def delete_belt_route(belt_id):
    if load_history_for_belt(belt_id):
        flash('Cannot delete a belt that has a championship history.', 'danger')
        return redirect(url_for('belts.list_belts'))
    success, message = delete_belt(belt_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('belts.list_belts'))

@belts_bp.route('/history/<string:belt_id>')
def history(belt_id):
    belt = get_belt_by_id(belt_id)
    if not belt:
        flash('Belt not found.', 'danger')
        return redirect(url_for('belts.list_belts'))
    history = sorted(load_history_for_belt(belt_id), key=lambda r: r.get('Date_Won', '0'), reverse=True)
    today = datetime.now().date()
    for reign in history:
        try:
            date_won = datetime.strptime(reign['Date_Won'], "%Y-%m-%d").date()
            date_lost = datetime.strptime(reign['Date_Lost'], "%Y-%m-%d").date() if reign.get('Date_Lost') else today
            reign['Days'] = (date_lost - date_won).days
        except (ValueError, TypeError): reign['Days'] = 'Error'
    return render_template('belts/history.html', belt=belt, history=history)

def _get_reign_form_data(form):
    return {
        'Belt_ID': form.get('belt_id'), 'Champion_Name': form.get('champion_name'),
        'Date_Won': form.get('date_won'), 'Date_Lost': form.get('date_lost') or None,
        'Defenses': form.get('defenses', 0, type=int), 'Notes': form.get('notes', '').strip()
    }

@belts_bp.route('/history/<string:belt_id>/add_reign', methods=['GET', 'POST'])
def add_reign(belt_id):
    belt = get_belt_by_id(belt_id)
    if not belt:
        flash('Belt not found.', 'danger')
        return redirect(url_for('belts.list_belts'))
    if request.method == 'POST':
        reign_data = _get_reign_form_data(request.form)
        success, message = add_reign_to_history(reign_data)
        flash(message, 'success' if success else 'danger')
        if success: return redirect(url_for('belts.history', belt_id=belt_id))
    return render_template('belts/reign_form.html', belt=belt, reign={}, form_action='create')

@belts_bp.route('/history/edit_reign/<string:reign_id>', methods=['GET', 'POST'])
def edit_reign(reign_id):
    reign = get_reign_by_id(reign_id)
    if not reign:
        flash('Reign not found.', 'danger')
        return redirect(url_for('belts.list_belts'))
    belt = get_belt_by_id(reign['Belt_ID'])
    if not belt:
        flash('Associated belt not found.', 'danger')
        return redirect(url_for('belts.list_belts'))
    if request.method == 'POST':
        updated_data = _get_reign_form_data(request.form)
        updated_data['Reign_ID'] = reign_id
        success, message = update_reign_in_history(reign_id, updated_data)
        flash(message, 'success' if success else 'danger')
        if success: return redirect(url_for('belts.history', belt_id=belt['ID']))
    return render_template('belts/reign_form.html', belt=belt, reign=reign, form_action='edit')

@belts_bp.route('/history/delete_reign/<string:reign_id>', methods=['POST'])
def delete_reign_route(reign_id):
    reign = get_reign_by_id(reign_id)
    if not reign:
        flash('Reign not found.', 'danger')
        return redirect(url_for('belts.list_belts'))
    belt_id = reign['Belt_ID']
    success, message = delete_reign_from_history(reign_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('belts.history', belt_id=belt_id))

