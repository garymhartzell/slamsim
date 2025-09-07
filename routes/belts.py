from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.belts import load_belts, add_belt, get_belt_by_id, update_belt, delete_belt
from src.wrestlers import load_wrestlers
from src.tagteams import load_tagteams
from src.segments import _slugify # For generating unique IDs
import uuid # For generating unique IDs

belts_bp = Blueprint('belts', __name__, url_prefix='/belts')

STATUS_OPTIONS = ['Active', 'Vacant']
HOLDER_TYPE_OPTIONS = ['Singles', 'Tag-Team']

def _get_form_data(form, is_create=False):
    """Extracts belt data from the form."""
    data = {
        'Name': form.get('name', '').strip(),
        'Status': form.get('status', '').strip(),
        'Holder_Type': form.get('holder_type', '').strip(),
        'Current_Holder': form.get('current_holder', '').strip()
    }
    if is_create:
        # Generate a unique ID for new belts
        base_id = _slugify(data['Name'])
        unique_suffix = str(uuid.uuid4())[:4]
        data['ID'] = f"{base_id}-{unique_suffix}"
    else:
        data['ID'] = form.get('belt_id', '').strip()

    return data

@belts_bp.route('/')
def list_belts():
    """Lists all belts."""
    all_belts = load_belts()
    return render_template('belts/list.html', belts=all_belts)

@belts_bp.route('/create', methods=['GET', 'POST'])
def create_belt():
    """Creates a new belt with an auto-generated ID."""
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
            else:
                flash(message, 'danger')
        return render_template('belts/form.html', belt=belt_data, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='create')

    return render_template('belts/form.html', belt={}, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='create')

@belts_bp.route('/edit/<string:belt_id>', methods=['GET', 'POST'])
def edit_belt(belt_id):
    """Edits an existing belt."""
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
            return render_template('belts/form.html', belt=belt_to_edit, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='edit')

        success, message = update_belt(belt_id, updated_data)
        if success:
            flash(message, 'success')
            return redirect(url_for('belts.list_belts'))
        else:
            flash(message, 'danger')
        return render_template('belts/form.html', belt=updated_data, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='edit')

    return render_template('belts/form.html', belt=belt_to_edit, status_options=STATUS_OPTIONS, holder_type_options=HOLDER_TYPE_OPTIONS, wrestlers=wrestlers, tagteams=tagteams, form_action='edit')


@belts_bp.route('/delete/<string:belt_id>', methods=['POST'])
def delete_belt_route(belt_id):
    """Deletes a belt."""
    success, message = delete_belt(belt_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('belts.list_belts'))

