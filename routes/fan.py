from flask import Blueprint, render_template

fan_bp = Blueprint('fan', __name__, url_prefix='/fan')

@fan_bp.route('/home')
def home():
    """Renders the fan home page."""
    return render_template('fan/home.html')
