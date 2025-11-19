import os
import markdown
from flask import Flask, render_template, url_for
from routes.divisions import divisions_bp
from routes.prefs import prefs_bp
from routes.wrestlers import wrestlers_bp
from routes.tagteams import tagteams_bp
from routes.events import events_bp
from routes.segments import segments_bp
from routes.belts import belts_bp
from routes.news import news_bp
from routes.booker import booker_bp # Import the new booker blueprint
from routes.fan import fan_bp       # Import the new fan blueprint
from routes.tools import tools_bp   # Import the new tools blueprint
from src.system import INCLUDES_DIR, LEAGUE_LOGO_FILENAME # Import INCLUDES_DIR and LEAGUE_LOGO_FILENAME

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages'
# Configure UPLOAD_FOLDER to be the 'includes' directory within the project root
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, INCLUDES_DIR)

# Register blueprints
app.register_blueprint(divisions_bp)
app.register_blueprint(prefs_bp)
app.register_blueprint(wrestlers_bp)
app.register_blueprint(tagteams_bp)
app.register_blueprint(events_bp)
app.register_blueprint(segments_bp)
app.register_blueprint(belts_bp)
app.register_blueprint(news_bp)
app.register_blueprint(booker_bp) # Register the booker blueprint
app.register_blueprint(fan_bp)     # Register the fan blueprint
app.register_blueprint(tools_bp)   # Register the tools blueprint

# Register a custom Jinja2 filter for markdown
@app.template_filter('markdown')
def markdown_filter(text):
    return markdown.markdown(text)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template('about.html')

@app.route('/goodbye')
def goodbye():
    """Renders the goodbye page."""
    return render_template('goodbye.html')

if __name__ == '__main__':
    app.run(debug=True)

