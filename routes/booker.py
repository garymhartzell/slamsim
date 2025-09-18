from flask import Blueprint, render_template

booker_bp = Blueprint('booker', __name__, url_prefix='/booker')

@booker_bp.route('/dashboard')
def dashboard():
    """Renders the booker dashboard page."""
    return render_template('booker/dashboard.html')
