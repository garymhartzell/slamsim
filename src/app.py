from flask import Flask, render_template
from routes.divisions import divisions_bp
from routes.prefs import prefs_bp
from routes.wrestlers import wrestlers_bp
from routes.tagteams import tagteams_bp
from routes.events import events_bp
from routes.segments import segments_bp
from routes.belts import belts_bp # Import the new belts blueprint

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages'

# Register blueprints
app.register_blueprint(divisions_bp)
app.register_blueprint(prefs_bp)
app.register_blueprint(wrestlers_bp)
app.register_blueprint(tagteams_bp)
app.register_blueprint(events_bp)
app.register_blueprint(segments_bp)
app.register_blueprint(belts_bp) # Register the new belts blueprint

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

