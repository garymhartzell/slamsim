from flask import Flask, render_template
from routes.divisions import divisions_bp # Import the divisions blueprint
from routes.prefs import prefs_bp # Import the preferences blueprint
from routes.wrestlers import wrestlers_bp # Import the wrestlers blueprint
from routes.tagteams import tagteams_bp # Import the tagteams blueprint

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages' # Required for flash messages

# Register blueprints
app.register_blueprint(divisions_bp)
app.register_blueprint(prefs_bp)
app.register_blueprint(wrestlers_bp)
app.register_blueprint(tagteams_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
