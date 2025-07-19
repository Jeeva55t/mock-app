from flask import Flask, render_template, request, session, redirect, url_for
import google.generativeai as genai
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24) 

try:
    genai.configure(api_key="")
except AttributeError:
    print("⚠️ Gemini API key not found in environment variables.")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            topic = request.form['topic']
            num_questions = int(request.form['num_questions'])
            difficulty = request.form['difficulty']

            prompt = f"""
            Generate a {num_questions}-question multiple-choice quiz on the topic of '{topic}' at a '{difficulty}' level.
            Provide your response as a JSON object. The object should have a single key "questions" which is an array.
            Each element in the array should be an object with three keys: "question_text", "options", and "correct_answer".
            "options" should be an array of 4 strings. "correct_answer" must be one of those 4 strings.

            Example format:
            {{
              "questions": [
                {{
                  "question_text": "What is the capital of France?",
                  "options": ["London", "Berlin", "Paris", "Madrid"],
                  "correct_answer": "Paris"
                }}
              ]
            }}
            """

            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
            quiz_data = json.loads(cleaned_response)
            
            session['questions'] = quiz_data['questions']

            return render_template('index.html', quiz=quiz_data['questions'])

        except Exception as e:
            error_message = f"An error occurred: {e}"
            return render_template('index.html', error=error_message)

   
    return render_template('index.html', quiz=None)



@app.route('/submit', methods=['POST'])
def submit():
    user_answers = request.form
    questions = session.get('questions', [])
    if not questions:
        return redirect(url_for('index')) 
    correct_answers_count = 0
    results_data = [] 
    for i, question_data in enumerate(questions):
        user_answer = user_answers.get(f'question-{i}')
        is_correct = (user_answer == question_data['correct_answer'])
        if is_correct:
            correct_answers_count += 1
        
        results_data.append({
            'question_text': question_data['question_text'],
            'options': question_data['options'],
            'user_answer': user_answer,
            'correct_answer': question_data['correct_answer'],
            'is_correct': is_correct
        })
            
    score = {
        "total": len(questions),
        "correct": correct_answers_count
    }
    
    session.pop('questions', None)
    
    return render_template('results.html', score=score, results=results_data)

@app.route('/explain', methods=['POST'])
def explain():
    data = request.get_json()
    question = data.get('question')
    user_answer = data.get('user_answer')
    correct_answer = data.get('correct_answer')
    
    if not all([question, user_answer, correct_answer]):
        return {"error": "Missing data"}, 400
        
    try:
        prompt = f"""
        For the following multiple-choice question:
        "{question}"

        Please explain in a concise and easy-to-understand way why the answer '{user_answer}' is incorrect, 
        and why '{correct_answer}' is the correct answer.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return {"explanation": response.text}
        
    except Exception as e:
        print(f"Error during explanation generation: {e}")
        return {"error": "Failed to generate explanation."}, 500

if __name__ == '__main__':
    app.run(debug=True)