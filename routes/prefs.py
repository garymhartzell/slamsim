from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.prefs import load_preferences, save_preferences
from src.wrestlers import reset_all_wrestler_records
from src.tagteams import reset_all_tagteam_records
from src.system import delete_all_league_data, delete_all_temporary_files

prefs_bp = Blueprint('prefs', __name__, url_prefix='/prefs')

@prefs_bp.route('/', methods=['GET', 'POST'])
def general_prefs():
    if request.method == 'POST':
        league_name = request.form.get('league_name', '').strip()
        league_short = request.form.get('league_short', '').strip()
        updated_prefs = {"league_name": league_name, "league_short": league_short}
        save_preferences(updated_prefs)
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('prefs.general_prefs'))
    
    prefs = load_preferences()
    return render_template('prefs.html', prefs=prefs)

@prefs_bp.route('/reset-records', methods=['POST'])
def reset_records():
    """Handles the resetting of all wrestler and tag team records."""
    if request.form.get('confirmation') == 'RESET':
        reset_all_wrestler_records()
        reset_all_tagteam_records()
        flash('All wrestler and tag team win/loss records have been reset to 0.', 'success')
    else:
        flash('Confirmation text was incorrect. Records were not reset.', 'danger')
    return redirect(url_for('prefs.general_prefs'))

@prefs_bp.route('/delete-league', methods=['POST'])
def delete_league():
    """Handles the complete deletion of all league data."""
    if request.form.get('confirmation') == 'DELETE':
        if delete_all_league_data():
            flash('All league data has been permanently deleted.', 'success')
        else:
            flash('An error occurred while deleting league data.', 'danger')
    else:
        flash('Confirmation text was incorrect. League data was not deleted.', 'danger')
    return redirect(url_for('prefs.general_prefs'))

@prefs_bp.route('/clear-temp-files', methods=['POST'])
def clear_temp_files():
    """Handles the deletion of all temporary files."""
    if request.form.get('confirmation') == 'CLEAR':
        if delete_all_temporary_files():
            flash('All temporary files (segment summaries) have been deleted.', 'success')
        else:
            flash('An error occurred while clearing temporary files.', 'danger')
    else:
        flash('Confirmation text was incorrect. Temporary files were not cleared.', 'danger')
    return redirect(url_for('prefs.general_prefs'))

