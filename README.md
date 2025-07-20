# 🧠 AI Quiz Generator

A simple Flask web app that uses the Gemini AI API to generate quizzes based on any topic. Users can create, take, and review quizzes with AI-generated questions and explanations.

---

## ✨ Features

- User login and registration
- Generate quizzes using Google Gemini API
- Choose topic, number of questions, and difficulty
- Automatic scoring and explanation for answers
- View quiz history

---

## 🛠 Tech Stack

- Python, Flask
- Gemini AI (Google Generative AI)
- SQLite (database)
- Tailwind CSS (frontend styling)

---

## 🚀 Getting Started

### 1. Clone the project

```bash
git clone https://github.com/Jeeva55t/mock-quizz-app.git
cd ai-quiz-generator
2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
3. Set your Gemini API key
In app.py:

python
Copy
Edit
import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")
Or set it as an environment variable:

bash
Copy
Edit
export GOOGLE_API_KEY="YOUR_API_KEY"  # Linux/macOS
set GOOGLE_API_KEY=YOUR_API_KEY       # Windows
4. Run the app
bash
Copy
Edit
flask run
Open http://localhost:5000 in your browser.
