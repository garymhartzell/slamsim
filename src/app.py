from flask import Flask, render_template
from routes.prefs import prefs_bp # Import the preferences blueprint

app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = 'a_very_secret_key_for_flash_messages' # Required for flash messages

# Register blueprints
app.register_blueprint(prefs_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
