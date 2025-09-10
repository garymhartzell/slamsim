from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.divisions import (
    load_divisions, add_division, get_division_by_id, 
    update_division, delete_division, is_division_in_use, get_all_division_ids_and_names
)

divisions_bp = Blueprint('divisions', __name__, url_prefix='/divisions')

STATUS_OPTIONS = ['Active', 'Inactive']

def _get_form_data(form):
    """Extracts division data from the form."""
    return {
        'ID': form.get('division_id', '').strip(),
        'Name': form.get('name', '').strip(),
        'Status': form.get('status', '').strip()
    }

@divisions_bp.route('/')
def list_divisions():
    """Lists all divisions and checks if they are deletable."""
    all_divisions = load_divisions()
    for division in all_divisions:
        division['is_deletable'] = not is_division_in_use(division['ID'])
    return render_template('divisions/list.html', divisions=all_divisions)

@divisions_bp.route('/create', methods=['GET', 'POST'])
def create_division():
    """Creates a new division."""
    if request.method == 'POST':
        division_data = _get_form_data(request.form)
        if not all(division_data.values()):
            flash('All fields are required.', 'danger')
        else:
            success, message = add_division(division_data)
            if success:
                flash(message, 'success')
                return redirect(url_for('divisions.list_divisions'))
            else:
                flash(message, 'danger')
    return render_template('divisions/form.html', division={}, status_options=STATUS_OPTIONS, form_action='create')

@divisions_bp.route('/edit/<string:division_id>', methods=['GET', 'POST'])
def edit_division(division_id):
    """Edits an existing division."""
    division_to_edit = get_division_by_id(division_id)
    if not division_to_edit:
        flash('Division not found.', 'danger')
        return redirect(url_for('divisions.list_divisions'))

    if request.method == 'POST':
        updated_data = _get_form_data(request.form)
        if not all(updated_data.values()):
            flash('All fields are required.', 'danger')
        else:
            if updated_data['ID'] != division_id:
                flash('Division ID cannot be changed.', 'danger')
            else:
                success, message = update_division(division_id, updated_data)
                if success:
                    flash(message, 'success')
                    return redirect(url_for('divisions.list_divisions'))
                else:
                    flash(message, 'danger')
    
    return render_template('divisions/form.html', division=division_to_edit, status_options=STATUS_OPTIONS, form_action='edit')


@divisions_bp.route('/view/<string:division_id>')
def view_division(division_id):
    """Views details of a single division."""
    division_data = get_division_by_id(division_id)
    if not division_data:
        flash('Division not found.', 'danger')
        return redirect(url_for('divisions.list_divisions'))
    return render_template('divisions/view.html', division=division_data)


@divisions_bp.route('/delete/<string:division_id>', methods=['POST'])
def delete_division_route(division_id):
    """Deletes a division only if it's not in use."""
    if is_division_in_use(division_id):
        flash('Cannot delete a division that is currently assigned to wrestlers.', 'danger')
        return redirect(url_for('divisions.list_divisions'))
    
    success, message = delete_division(division_id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('divisions.list_divisions'))

