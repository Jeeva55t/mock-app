from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-very-secret-key-that-is-long-and-random' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


genai.configure(api_key="")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    quizzes = db.relationship('QuizHistory', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class QuizHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(150), nullable=False)
    score_correct = db.Column(db.Integer, nullable=False)
    score_total = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    questions = db.relationship('QuestionHistory', backref='quiz', lazy=True, cascade="all, delete-orphan")

class QuestionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False) 
    user_answer = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz_history.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
        else: flash('Invalid username or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash('Username already exists. Please choose a different one.', 'error')
        else:
            new_user = User(username=request.form['username'])
            new_user.set_password(request.form['password'])
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        try:
            session['quiz_topic'] = request.form['topic'] 
            num_questions = int(request.form['num_questions'])
            difficulty = request.form['difficulty']
            prompt = f"""
            Generate a {num_questions}-question multiple-choice quiz on the topic of '{session['quiz_topic']}' at a '{difficulty}' level.
            Provide your response as a JSON object with a single key "questions" which is an array of objects.
            Each object must have "question_text", "options" (an array of 4 strings), and "correct_answer" keys.
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
@login_required
def submit():
    user_answers = request.form
    questions = session.get('questions', [])
    quiz_topic = session.get('quiz_topic', 'General')
    if not questions: return redirect(url_for('index'))
    
    correct_answers_count = 0
    results_data = []
    for i, q_data in enumerate(questions):
        user_answer = user_answers.get(f'question-{i}')
        is_correct = (user_answer == q_data['correct_answer'])
        if is_correct: correct_answers_count += 1
        results_data.append({
            'question_text': q_data['question_text'], 'options': q_data['options'],
            'user_answer': user_answer, 'correct_answer': q_data['correct_answer'], 'is_correct': is_correct
        })
        
    score = {"total": len(questions), "correct": correct_answers_count}

    try:
        new_quiz_history = QuizHistory(
            topic=quiz_topic,
            score_correct=score['correct'],
            score_total=score['total'],
            user_id=current_user.id
        )
        db.session.add(new_quiz_history)
        db.session.flush() 

        for res in results_data:
            new_question = QuestionHistory(
                question_text=res['question_text'],
                options=json.dumps(res['options']),
                user_answer=res['user_answer'],
                correct_answer=res['correct_answer'],
                is_correct=res['is_correct'],
                quiz_id=new_quiz_history.id
            )
            db.session.add(new_question)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error saving to DB: {e}")
        flash('There was an error saving your quiz results.', 'error')
    
    session.pop('questions', None)
    session.pop('quiz_topic', None)
    
    return render_template('results.html', score=score, results=results_data)

@app.route('/history')
@login_required
def history():
    user_quizzes = QuizHistory.query.filter_by(user_id=current_user.id).order_by(QuizHistory.timestamp.desc()).all()
    return render_template('history.html', quizzes=user_quizzes)

@app.route('/history/<int:quiz_id>')
@login_required
def history_detail(quiz_id):
    quiz = QuizHistory.query.get_or_404(quiz_id)
    if quiz.user_id != current_user.id:
        flash("You are not authorized to view this page.", "error")
        return redirect(url_for('history'))

    results_data = []
    for q in quiz.questions:
        results_data.append({
            'question_text': q.question_text,
            'options': json.loads(q.options), 
            'user_answer': q.user_answer,
            'correct_answer': q.correct_answer,
            'is_correct': q.is_correct
        })
    
    score = {"total": quiz.score_total, "correct": quiz.score_correct}
    return render_template('results.html', score=score, results=results_data, from_history=True)


@app.route('/explain', methods=['POST'])
@login_required
def explain():
    
    data = request.get_json()
    question, user_answer, correct_answer = data.get('question'), data.get('user_answer'), data.get('correct_answer')
    if not all([question, user_answer, correct_answer]): return {"error": "Missing data"}, 400
    try:
        prompt = f"""For the question: "{question}"\nExplain why '{user_answer}' is incorrect, and why '{correct_answer}' is correct."""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"explanation": response.text}
    except Exception as e:
        print(f"Error during explanation generation: {e}")
        return {"error": "Failed to generate explanation."}, 500


@app.route('/history/delete/<int:quiz_id>', methods=['POST'])
@login_required
def delete_history(quiz_id):
    quiz_to_delete = QuizHistory.query.get_or_404(quiz_id)
    
    if quiz_to_delete.user_id != current_user.id:
        flash("You are not authorized to perform this action.", "error")
        return redirect(url_for('history'))
        
    try:
        db.session.delete(quiz_to_delete)
        db.session.commit()
        flash('Quiz history entry deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting history: {e}")
        flash('There was an error deleting the history entry.', 'error')
        
    return redirect(url_for('history'))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)