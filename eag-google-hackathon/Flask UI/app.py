from flask import Flask, render_template, request

app = Flask(__name__)

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get form data
        survey_type = request.form.get('survey_type')
        survey_details = request.files['survey_details']
        participant_info = request.files['participant_info']
        survey_mode = request.form.get('survey_mode')

        # Process the form data
        # Generate the survey based on the provided inputs
        # Your code for generating the survey goes here

        return "Survey generated successfully!"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
