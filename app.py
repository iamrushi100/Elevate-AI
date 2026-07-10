# app.py
import os

# ✅ Set BEFORE importing pytesseract
os.environ["TESSDATA_PREFIX"] = r"C:\Users\ADMIN\scoop\apps\tesseract\current\tessdata"

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
import pytesseract

# ✅ Set tesseract path after import
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ADMIN\scoop\apps\tesseract\current\tesseract.exe"

class WeakTopicRequest(BaseModel):
    mistakes: str
    subject: str
    unit: str
class AnswerEvaluationRequest(BaseModel):
    question: str
    user_answer: str
from rag import get_retriever
from llm import run_llm

available_diagrams = [
    "centralized_distributed.png",
    "modern_data_centre.png",
    "openflow_controller.png",
    "openflow_pipelining_process.png",
    "openflow_protocol.png",
    "openflow.png",
    "sdn_architecture.png",
    "sdn_controller.png"
]

# Create FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Load retriever (your AI memory)
retriever = get_retriever()

# Input model
class Query(BaseModel):
    question: str

# -------- MAIN Q&A API --------
@app.post("/ask")
def ask(query: Query):
    try:
        # Step 1: Retrieve context
        docs = retriever.invoke(query.question)
        context = " ".join([doc.page_content for doc in docs])

        # Step 2: Generate answer ✅
        prompt = f"""
You are an SPPU Engineering Exam Assistant.
Your task is to:

1. First analyze PYQ relevance briefly
2. Then explain the concept properly like a teacher
3. Give exam-oriented structured answer

STRICT RESPONSE FORMAT:

Do 2 things:

1. PYQ Analysis:
- Check if this question is asked in previous university exams
- If YES:
    - Show PYQ Status: Asked
    - Show how many times repeated
    - Show years
    - Show exact PYQ question
- If NO:
    - Show PYQ Status: Not Asked

2. Generate PERFECT 8-mark answer (exam writing format):

STRICT FORMAT:

PYQ:
Status: ...
Times Asked: ...
Years: ...
Question: ...

ANSWER:

Introduction:
- Point 1
- Point 2
- Point 3

Explanation:

1. Topic heading
- Point
- Point

2. Topic heading
- Point
- Point

3. Topic heading
- Point
- Point

Advantages:
- Short point
- Short point
- Short point

Disadvantages:
- Short point
- Short point
- Short point

Example:
- One real-world example

Diagram:
- Mention what diagram to draw

Rules:
- Do NOT answer only PYQ analysis
- Use simple exam language
- No HTML tags
- No paragraphs
- Only bullet points
- Explanation must be divided into sub-parts
- Use keywords like Packet-In, Flow-Mod, Controller
- Answer should look like written in exam paper
- Do NOT add extra text

Question: {query.question}
Context: {context}
"""

        answer = run_llm(prompt)
        # -------- SPLIT PYQ + ANSWER --------
        pyq_part = ""
        answer_part = answer

        if "ANSWER:" in answer:
            parts = answer.split("ANSWER:")
            pyq_part = parts[0].strip()
            answer_part = parts[1].strip()

        # -------- HYBRID DIAGRAM SYSTEM --------

        # 1. Keyword mapping
        diagram_map = {
            "sdn": "sdn_architecture.png",
            "architecture": "sdn_architecture.png",
            "controller": "sdn_controller.png",
            "openflow": "openflow.png",
            "protocol": "openflow_protocol.png",
            "pipeline": "openflow_pipelining_process.png",
        }

        diagram = None
        q = query.question.lower()

        for key in diagram_map:
            if key in q:
                diagram = diagram_map[key]
                break

        # 2. AI fallback
        if diagram is None:
            diagram_prompt = f"""
User question: {query.question}

Available diagrams:
{available_diagrams}

Return ONLY exact file name or NONE.
"""
            diagram_response = run_llm(diagram_prompt).strip()

            if "none" not in diagram_response.lower():
                temp = diagram_response.replace('"', '').strip()
                if temp in available_diagrams:
                    diagram = temp

        # -------- FINAL RESPONSE --------
        return {
            "pyq": pyq_part,
            "answer": answer_part,
            "diagram": diagram
        }

    except Exception as e:
        return {"ERROR": str(e)}
    
@app.post("/voice-ask")
def voice_ask(query: Query):
    try:
        docs = retriever.invoke(query.question)
        context = " ".join([doc.page_content for doc in docs])

        prompt = f"""
You are a friendly AI engineering tutor.

Answer the student's question conversationally.

RULES:
- Maximum 120 words
- Short spoken-style answer
- Easy language
- Explain clearly
- Avoid long bullet lists
- Avoid exam formatting
- Keep it natural for voice conversation

Question:
{query.question}

Context:
{context}
"""

        answer = run_llm(prompt)

        return {
            "answer": answer
        }

    except Exception as e:
        return {"ERROR": str(e)}
# -------- REVISION API --------
@app.get("/revision")
def revision(subject: str, unit: str):
    try:
        # Fetch real PYQs from vectorstore
        docs = retriever.invoke(f"previous year questions {subject} {unit}")
        pyq_context = " ".join([doc.page_content for doc in docs])

        prompt = f"""
You are an SPPU Engineering Exam Assistant.

Real Previous Year Questions (USE ONLY THESE, DO NOT MAKE UP ANY):
{pyq_context}

Generate revision for:
Subject: {subject}
Unit: {unit}

STRICT FORMAT:

1. PYQ-Based Revision:
- List ONLY questions from the PYQ data above
- For EACH question:
    • Exact question text
    • Years asked (from PYQ data only)
    • Times repeated
    • Short answer (5-6 bullet points)

2. Important Concepts (not in PYQ):
- Short bullet notes

3. Important Keywords:
- keyword: one line meaning

4. Exam Tips:
- Short practical tips

RULES:
- DO NOT invent years or questions
- ONLY use questions from PYQ data provided
- Keep answers short and exam-ready
"""

        answer = run_llm(prompt)
        return {"revision": answer}

    except Exception as e:
        return {"ERROR": str(e)}
    
@app.get("/generate-quiz")
def generate_quiz(subject: str, unit: str):
    try:
        # Fetch real PYQs
        docs = retriever.invoke(f"previous year questions {subject} {unit}")
        pyq_context = " ".join([doc.page_content for doc in docs])

        prompt = f"""
You are an SPPU exam setter.

Real PYQ Questions (USE THESE ONLY, DO NOT MAKE UP):
{pyq_context}

Generate 10 MCQ questions for:
Subject: {subject}
Unit: {unit}

RULES:
- At least 7 questions MUST be based on real PYQs above
- Tag PYQ questions with [PYQ] at the start
- Tag non-PYQ questions with [CONCEPT]
- Each question must have 4 options (A, B, C, D)
- Only ONE correct answer per question

STRICT FORMAT:

Q1. [PYQ] Question here
A. option
B. option
C. option
D. option

Q2. [CONCEPT] Question here
A. option
B. option
C. option
D. option

(continue till Q10)

---END QUESTIONS---

ANSWERS:
1-A
2-C
(continue till 10)
"""
        quiz = run_llm(prompt)
        return {"quiz": quiz}

    except Exception as e:
        return {"ERROR": str(e)}
    

class QuizEvaluation(BaseModel):
    quiz: str
    user_answers: str


@app.post("/evaluate-quiz")
def evaluate_quiz(data: QuizEvaluation):
    try:
        prompt = f"""
You are an SPPU exam evaluator.

Quiz:
{data.quiz}

User Answers:
{data.user_answers}

STRICT FORMAT:

SCORE: X/10

RESULT TABLE:
Q1: User answered [X] | Correct: [Y] | ✔ or ✘
Q2: User answered [X] | Correct: [Y] | ✔ or ✘
(continue for all 10)

WRONG ANSWERS EXPLAINED:
(Only for wrong answers)
Q#:
- Correct Answer:
- Why it's correct: (1-2 lines)
- Why user's answer is wrong: (1 line)

WEAK TOPICS:
- Topic 1
- Topic 2

SUGGESTIONS:
- What to study next
"""

        result = run_llm(prompt)

        # -------- SAVE TO JSON (CORRECT) --------
        import json
        import os

        file_path = os.path.join(os.path.dirname(__file__), "user_data.json")

        try:
            with open(file_path, "r") as f:
                data_store = json.load(f)
        except:
            data_store = {}

        user_id = "default_user"

        # Append new result
        data_store[user_id] = data_store.get(user_id, []) + [result]

        with open(file_path, "w") as f:
            json.dump(data_store, f, indent=4)

        print("✅ Data saved successfully:", data_store)

        # -------- RETURN RESPONSE --------
        return {"result": result}

    except Exception as e:
        return {"ERROR": str(e)}

@app.post("/weak-analysis")
def weak_analysis(data: WeakTopicRequest):
    try:
        import json

        try:
            with open("user_data.json", "r") as f:
                data_store = json.load(f)
        except:
            data_store = {}

        user_id = "default_user"

        history = data_store.get(user_id, [])
        history_text = "\n".join(history)

        prompt = f"""
You are an SPPU learning assistant.

Analyze student's performance using:

Previous Quiz History:
{history_text}

User Request:
{data.mistakes}

Subject: {data.subject}
Unit: {data.unit}

Do:

1. Identify repeated weak topics
2. Rank them (most weak → least)
3. Explain why they are important (PYQ relevance)
4. Suggest what to study first
5. Give improvement strategy

6. If user asked a topic explicitly, explain it in simple terms

Make it structured and practical.
"""

        analysis = run_llm(prompt)

        return {"analysis": analysis}

    except Exception as e:
        return {"ERROR": str(e)}

@app.post("/evaluate-answer-image")
def evaluate_answer_image(file: UploadFile = File(...), question: str = ""):
    try:
        image = Image.open(file.file)

        # OCR
        extracted_text = pytesseract.image_to_string(
    image,
    lang="eng"
)

        prompt = f"""
You are an SPPU evaluator.

Question:
{question}

Student Answer (from image):
{extracted_text}

Evaluate like strict examiner.

Give:
1. Marks out of 8
2. Mistakes
3. Improvements
4. Better structure
"""

        result = run_llm(prompt)

        return {
            "extracted_text": extracted_text,
            "evaluation": result
        }

    except Exception as e:
        return {"ERROR": str(e)}
    
@app.post("/evaluate-answer")
def evaluate_answer(data: AnswerEvaluationRequest):
    try:
        prompt = f"""
You are an SPPU strict examiner.

Question:
{data.question}

Student Answer:
{data.user_answer}

Evaluate based on:

1. Marks (out of 8)

2. Structure:
- Introduction
- Explanation
- Advantages/Disadvantages
- Example

3. Mistakes:
- Missing keywords
- Wrong concepts

4. Improvements:
- What to add
- How to improve

Give clear and structured feedback.
"""

        result = run_llm(prompt)

        return {"evaluation": result}

    except Exception as e:
        return {"ERROR": str(e)}
    
@app.get("/generate-practice-question")
def generate_practice_question(subject: str = "SDN", unit: str = ""):
    try:
        docs = retriever.invoke(f"previous year questions PYQ {subject} {unit}")
        context = " ".join([doc.page_content for doc in docs])

        prompt = f"""
You are an SPPU exam setter.

Below are Previous Year Questions (PYQ):
{context}

Task:
- Pick ONE random 8-mark question from the PYQ list above
- Check how many times it was repeated across years
- Output STRICTLY in this format:

Question: <question>
Asked in: <Apr'2023 / Mar'2024 / Mar'2025>
Times Repeated: <number>

No extra text. No explanation.
"""
        question = run_llm(prompt)
        return {"question": question}

    except Exception as e:
        return {"ERROR": str(e)}
    
class WrongAnswerRequest(BaseModel):
    question: str
    user_answer: str
    correct_answer: str

@app.post("/explain-wrong")
def explain_wrong(data: WrongAnswerRequest):
    try:
        prompt = f"""
You are an SPPU exam teacher.

Question: {data.question}
Student answered: {data.user_answer}
Correct answer: {data.correct_answer}

Give:
1. Why correct answer is right (2-3 lines, simple language)
2. Why student's answer is wrong (1 line)

Keep it short and exam-focused.
No bullet symbols, just plain text.
"""
        result = run_llm(prompt)
        return {"explanation": result}

    except Exception as e:
        return {"ERROR": str(e)}