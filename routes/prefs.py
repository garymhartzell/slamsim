from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.prefs import load_preferences, save_preferences

prefs_bp = Blueprint('prefs', __name__, url_prefix='/prefs')

@prefs_bp.route('/', methods=['GET', 'POST'])
def general_prefs():
    if request.method == 'POST':
        league_name = request.form.get('league_name', '').strip()
        league_short = request.form.get('league_short', '').strip()

        updated_prefs = {
            "league_name": league_name,
            "league_short": league_short
        }
        save_preferences(updated_prefs)
        flash('Preferences updated successfully!', 'success')
        return redirect(url_for('prefs.general_prefs'))
    
    prefs = load_preferences()
    return render_template('prefs.html', prefs=prefs)
