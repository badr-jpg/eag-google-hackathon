from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.auth import credentials
from google.oauth2 import service_account
import google.cloud.aiplatform as aiplatform
from vertexai.preview.language_models import ChatModel, InputOutputTextPair, TextGenerationModel
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import vertexai
import json  # add this line
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

    file_path = "response.txt"  # Replace with the actual path to your file
    with open(file_path, "w") as file:
        file.write(str(response))


    # Return the model's response
    return {"response": response.text}