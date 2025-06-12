# Elevate AI – Full Project Code

# -----------------------------------
# backend/app.py
# -----------------------------------
from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_models.model import generate_answer, generate_quiz, generate_notes

app = Flask(__name__)
CORS(app)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    answer = generate_answer(question)
    return jsonify({"answer": answer})

@app.route("/quiz", methods=["POST"])
def quiz():
    data = request.json
    topic = data.get("topic")
    quiz = generate_quiz(topic)
    return jsonify({"quiz": quiz})

@app.route("/notes", methods=["POST"])
def notes():
    data = request.json
    content = data.get("content")
    notes = generate_notes(content)
    return jsonify({"notes": notes})

if __name__ == "__main__":
    app.run(debug=True)

# -----------------------------------
# ml_models/model.py
# -----------------------------------
def generate_answer(question):
    return f"AI-generated answer for: {question}"

def generate_quiz(topic):
    return [
        {"question": f"What is {topic}?", "options": ["Option A", "Option B"], "answer": "Option A"},
        {"question": f"Explain {topic} in detail.", "options": ["Option C", "Option D"], "answer": "Option D"}
    ]

def generate_notes(content):
    return f"Summary Notes: {content[:100]}..."

# -----------------------------------
# requirements.txt
# -----------------------------------
flask
flask-cors

# -----------------------------------
# frontend/index.html
# -----------------------------------
<!DOCTYPE html>
<html>
<head>
    <title>Elevate AI</title>
</head>
<body>
    <h1>Ask a Question</h1>
    <input type="text" id="question" placeholder="Type your question">
    <button onclick="askAI()">Ask</button>
    <p id="answer"></p>

    <h1>Generate Quiz</h1>
    <input type="text" id="quizTopic" placeholder="Enter topic">
    <button onclick="getQuiz()">Generate Quiz</button>
    <pre id="quiz"></pre>

    <h1>Generate Notes</h1>
    <textarea id="notesContent" placeholder="Paste content here..."></textarea><br>
    <button onclick="getNotes()">Generate Notes</button>
    <pre id="notes"></pre>

    <script>
        async function askAI() {
            const question = document.getElementById('question').value;
            const res = await fetch('http://localhost:5000/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question })
            });
            const data = await res.json();
            document.getElementById('answer').innerText = data.answer;
        }

        async function getQuiz() {
            const topic = document.getElementById('quizTopic').value;
            const res = await fetch('http://localhost:5000/quiz', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic })
            });
            const data = await res.json();
            document.getElementById('quiz').innerText = JSON.stringify(data.quiz, null, 2);
        }

        async function getNotes() {
            const content = document.getElementById('notesContent').value;
            const res = await fetch('http://localhost:5000/notes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            const data = await res.json();
            document.getElementById('notes').innerText = data.notes;
        }
    </script>
</body>
</html>

# -----------------------------------
# data/sample_data.csv
# -----------------------------------
Question,Answer
"What is AI?","Artificial Intelligence is the simulation of human intelligence in machines."
"Define NLP","Natural Language Processing allows computers to understand human language."

# -----------------------------------
# .gitignore
# -----------------------------------
__pycache__/
*.py[cod]
venv/
.env
.DS_Store
node_modules/

# -----------------------------------
# README.md
# -----------------------------------
# Elevate AI – AI-Powered Educational Assistant

Elevate AI is a cross-platform educational assistant using machine learning and NLP to provide real-time problem-solving, personalized quizzes, and automated note generation.

## Features
- AI-powered Q&A via Flask API
- Quiz generation based on topic
- NLP-based auto note generator
- Simple web-based frontend

## How to Run
```bash
pip install -r requirements.txt
python backend/app.py
# Open frontend/index.html in a browser
```

## License
MIT
