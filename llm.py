import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

print("API KEY:", os.getenv("GROQ_API_KEY"))

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

def run_llm(prompt):
    response = llm.invoke(prompt)
    return response.content