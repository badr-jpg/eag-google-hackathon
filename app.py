from flask import Flask, render_template, request, redirect, url_for
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.auth import credentials
from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, TextGenerationModel
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import vertexai
import json  # add this line
import pandas as pd
import os

# Load the service account json file
# Update the values in the json file with your own
with open(
    "service_account.json"
) as f:  # replace 'serviceAccount.json' with the path to your file if necessary
    service_account_info = json.load(f)

my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)

# Initialize Google AI Platform with project details and credentials
aiplatform.init(
    credentials=my_credentials,
)

with open("service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]


# Initialize Vertex AI with project and location
vertexai.init(project=project_id, location="us-central1")

app = Flask(__name__)

# Routes
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/admin', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get form data
        survey_details = request.form.get('survey_details')
        participant_info = request.files['participant_info']
        goal = request.form.get('goal')
        survey_mode = request.form.get('survey_mode')

        # Process the form data
        # Generate the survey based on the provided inputs
        # Your code for generating the survey goes here
        generate_surveys(survey_details, goal, 10)
        return "Survey generated successfully!"

    return render_template('admin.html')

@app.route('/user', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Process the survey responses
        res = ""
        survey_name = request.args.get('survey_name')
        if(survey_name == None):
            survey_name = 'Survey-Alex.txt'            
            
        result_file =  "Result-" + survey_name
        for key, value in request.form.items():
            # Store the responses or perform any necessary actions
            res = res + "\n" f"Question: {key}: Answer: {value}"
        
        with open(result_file, 'w') as f:
            f.write(res)
        analyze(1)
        return "Thank you for completing the survey!"
    
    else:
        survey_files = [filename for filename in os.listdir('.') if filename.startswith('Survey')]
        survey_strings = []
        for file in survey_files:
            with open(file, 'r') as f:
            # Process each survey file here
            # Example: Read the file contents
                contents = f.read()
                survey_strings.append((file, contents))
        file_path = request.args.get('survey_name')
        if(file_path == None):
            file_path = 'Survey-Alex.txt'  
        # request.args.set(survey_name='Survey-Alex.txt')
        jsons = read_jsons_from_file(file_path)
        questions = generate_survey_questions(jsons)
        return render_template('user.html', questions=questions, surveys=survey_strings)

@app.route('/survey')
def survey_sel():
    survey_name = request.args.get('name')
    # Load the survey file based on the survey_name variable
    # Process the survey data and pass it to the template
    # Return the rendered template with the survey data
    return redirect(url_for('survey', survey_name=survey_name))


@app.route('/survey_analysis')
def survey_analysis():
    # Load the survey file based on the survey_name variable
    # Process the survey data and pass it to the template
    # Return the rendered template with the survey data
    with open("SurveyAnalysis.txt", 'r') as file:
        analysis_txt = file.read()

    return render_template('survey_analysis.html', analysis_txt=analysis_txt)


#Functions

def read_jsons_from_file(file_path):
    jsons = []
    with open(file_path, 'r') as file:
        json_data = file.read()
        json_data = json_data.replace("```\n", "")
        json_data = json_data.replace("```", "")

        json_objects = json_data.strip().split('\n')
        
        
        for json_object in json_objects:
            if json_object == "":
                continue
            print(json_object)
            jsons.append(json.loads(json_object))
    
    return jsons

def generate_survey_questions(jsons):
    questions = []
    question_num = 1
    for json_data in jsons:
        question = json_data['Question']
        answer1 = json_data['answer1']
        answer2 = json_data['answer2']
        answer3 = json_data['answer3']
        answer4 = json_data['answer4']
        questions.append((question_num, question, answer1, answer2, answer3, answer4))
        question_num += 1
    
    return questions

def generate_surveys(survey_info, goal, numq):
    """
    Endpoint to handle chat.
    Receives a message from the user, processes it, and returns a response from the model.
    """
    # chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        "temperature": 0.9,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40,
    }
    # chat = chat_model.start_chat(  # Initialize the chat with model
    #     # chat context and examples go here
    # )
    # Build the prompt
    users_dets = pd.read_csv("UserDetails.csv")

    for index, row in users_dets.iterrows():

        with open("PromptSkeleton.txt", "r") as file:
            prompt = file.read()

        prompt_path = "full_prompt.txt"
        prompt = prompt.replace("<PD>", row['description'])
        prompt = prompt.replace("<SURVEY_INFO>", survey_info)
        prompt = prompt.replace("<NUM_QUESTIONS>", str(numq))
        prompt = prompt.replace("<GOAL>", goal) # "Determine how the participants felt about the challenge. Was it too hard, too easy, unclear? The questions should help us evaluate how well recieved the hackathon was."
        with open(prompt_path, "w") as file:
            file.write(str(prompt))

        # Send the human message to the model and get a response
        model = TextGenerationModel.from_pretrained("text-bison@001")
        response = model.predict(prompt, **parameters)
        # response = chat.send_message(prompt, **parameters)

        file_path = "Survey-" + str(row['name']) + ".txt"  # Replace with the actual path to your file
        with open(file_path, "w") as file:
            file.write(str(response))


def analyze(survey_id):
    """
    Endpoint to handle chat.
    Receives a message from the user, processes it, and returns a response from the model.
    """
    parameters = {
        "temperature": 0.9,
        "max_output_tokens": 1024,
        "top_p": 0.8,
        "top_k": 40,
    }

    survey_files = [filename for filename in os.listdir('.') if filename.startswith('Result')]
    results = ""

    for file in survey_files:
        with open(file, 'r') as f:
            results += f.read()
    
    with open("AnalysisPrompt.txt", "r") as file:
        prompt = file.read()
    
    prompt = prompt.replace("<QA>", results)
   
    # Send the human message to the model and get a response
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(prompt, **parameters)

    file_path = "SurveyAnalysis.txt"  # Replace with the actual path to your file
    with open(file_path, "w") as file:
        file.write(str(response))


    # Return the model's response
    return {"response": response.text}

if __name__ == '__main__':
    app.run(debug=True)
