# main.py
import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# Load environment variables from a .env file
load_dotenv()

# Define a Pydantic model for the request body
class TopicRequest(BaseModel):
    topic: str

    
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1))


@tool
def get_web_summary(topic: str) -> str:
    """
    Searches the web for the given topic and returns a summary.
    Input should be a simple topic, like "quantum computing".
    """
    try:
        search_result = wikipedia.run(topic)
        # You can add more complex logic here to summarize the search result if needed
        # For this example, we'll return the raw search result
        return search_result
    except Exception as e:
        return f"An error occurred: {e}"

app = FastAPI(
    title="AI Microservice",
    description="A service to summarize text and generate quizzes using LangChain."
)

# A simple endpoint to verify the service is running
@app.get("/")
async def read_root():
    return {"message": "AI service is online!"}

# Endpoint for web-based summarization
@app.post("/summarize-web")
async def summarize_web(request: TopicRequest):
    # This is where the LangChain web scraping and summarization logic will go
    # For now, we'll return a placeholder
    return {"summary": f"Placeholder summary for the topic: {request.topic}"}

# Endpoint for PDF summarization
@app.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    # This is where the LangChain PDF processing and summarization logic will go
    # For now, we'll return a placeholder
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")
    
    return {"summary": "Placeholder summary for the uploaded PDF."}

# Endpoint for combined summarization
@app.post("/summarize-combined")
async def summarize_combined(topic: str = Form(...), file: UploadFile = File(...)):
    # This is where the LangChain combined logic will go
    # For now, we'll return a placeholder
    return {"summary": "Placeholder summary for combined data."}

# Endpoint for quiz generation
@app.post("/generate-quiz")
async def generate_quiz(summary: str):
    # This is where the LangChain quiz generation logic will go
    # For now, we'll return a placeholder
    quiz_data = {
        "question": "What is the capital of France?",
        "options": ["Paris", "Berlin", "Rome"],
        "answer": "Paris"
    }
    return quiz_data