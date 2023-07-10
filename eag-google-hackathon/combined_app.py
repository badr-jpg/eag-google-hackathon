from flask import Flask, render_template
from FlaskUI import app as app1
from FlaskUserUI import app as app2

# Create the combined application
combined_app = Flask(__name__)

# Route for the homepage
@combined_app.route('/')
def index():
    return render_template('index.html')

# Route for app1
@combined_app.route('/app1')
def route_to_app1():
    return app1.home()

# Route for app2
@combined_app.route('/app2')
def route_to_app2():
    return app2.survey()

if __name__ == '__main__':
    # Run the combined application
    combined_app.run()

    