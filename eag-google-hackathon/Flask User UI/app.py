import json
from flask import Flask, request, render_template

app = Flask(__name__)

def read_jsons_from_file(file_path):
    jsons = []
    with open(file_path, 'r') as file:
        json_data = file.read()
        json_objects = json_data.strip().split('\n')
        
        for json_object in json_objects:
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

@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Process the survey responses
        for key, value in request.form.items():
            # Store the responses or perform any necessary actions
            print(f"Question {key}: {value}")
        
        return "Thank you for completing the survey!"
    
    else:
        file_path = '/home/ns/Documents/google-vertex-ai-hackathon/eag-google-hackathon-new/eag-google-hackathon/eag-google-hackathon/app/response.txt'
        jsons = read_jsons_from_file(file_path)
        questions = generate_survey_questions(jsons)
        print(questions)
        return render_template('survey.html', questions=questions)

if __name__ == '__main__':
    app.run()
