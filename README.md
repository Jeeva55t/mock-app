AI-Powered Adaptive Quiz Platform
An intelligent, full-stack web application that dynamically generates personalized mock tests using Google's Gemini API. This platform provides a secure, interactive, and adaptive learning environment for users to test and improve their knowledge on any subject.

Live Demo Link (https://mock-quizz-app.onrender.com)

Key Features
Dynamic Quiz Generation: Leverages the Google Gemini API to create unique multiple-choice quizzes on any user-specified topic and difficulty level.

Secure User Authentication: Full registration and login system with secure password hashing (werkzeug) and session management (Flask-Login).

Personalized User Dashboard: Provides users with at-a-glance analytics of their performance, including total quizzes taken, overall average score, and best-performing topic.

Comprehensive Test History: Persistently stores all past quiz results, allowing users to review their answers, track progress over time, and delete old entries.

AI-Powered Feedback: A unique "Explain My Mistake" feature makes a secondary API call to provide contextual, AI-generated explanations for incorrect answers, turning the app into an active learning tool.

Clean, Responsive Frontend: A user-friendly interface built with HTML, CSS, and JavaScript that works seamlessly on both desktop and mobile devices.

Tech Stack
Backend: Python, Flask

Database: SQLite, Flask-SQLAlchemy

Authentication: Flask-Login, Werkzeug

Frontend: HTML5, CSS3, JavaScript, Jinja2

AI Integration: Google Gemini API

Deployment:https://mock-quizz-app.onrender.com

Local Setup and Installation
Follow these steps to run the project on your local machine.

1. Clone the Repository
Bash

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.

Bash

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Install all the required libraries from the requirements.txt file.

Bash

pip install -r requirements.txt
(Note: To create a requirements.txt file, run pip freeze > requirements.txt in your activated virtual environment.)

4. Configure Environment Variables
The application requires a Gemini API key. It's best practice to set this as an environment variable.

For Windows (Command Prompt):

Bash

set GEMINI_API_KEY="YOUR_API_KEY_HERE"
For macOS/Linux:

Bash

export GEMINI_API_KEY="YOUR_API_KEY_HERE"
Alternatively, you can hardcode the key in app.py, but this is not recommended.

5. Run the Application
The app.py script will automatically create the users.db database file on the first run.

Bash

python app.py
The application will be available at http://127.0.0.1:5000
