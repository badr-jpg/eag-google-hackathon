from flask import Flask, render_template, request
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

# Load the service account json file
# Update the values in the json file with your own
with open(
    "FlaskUI/service_account.json"
) as f:  # replace 'serviceAccount.json' with the path to your file if necessary
    service_account_info = json.load(f)

my_credentials = service_account.Credentials.from_service_account_info(
    service_account_info
)

# Initialize Google AI Platform with project details and credentials
aiplatform.init(
    credentials=my_credentials,
)

with open("FlaskUI/service_account.json", encoding="utf-8") as f:
    project_json = json.load(f)
    project_id = project_json["project_id"]


# Initialize Vertex AI with project and location
vertexai.init(project=project_id, location="us-central1")

app = Flask(__name__)

# Routes
@app.route('/', methods=['GET', 'POST'])
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

    return render_template('index.html')

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
    

if __name__ == '__main__':
    app.run(debug=True)
