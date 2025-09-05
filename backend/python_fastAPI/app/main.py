import os
import shutil
import asyncio
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import List, Dict, Any, Union


from langchain_community.llms import OpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough


load_dotenv()

# Define Pydantic models for the API request bodies and responses
class TopicRequest(BaseModel):
    topic: str

class QuizRequest(BaseModel):
    summary: str

class Option(BaseModel):
    label: str = Field(..., description="The option label, e.g., 'A'")
    text: str = Field(..., description="The text of the option")

class Question(BaseModel):
    question: str = Field(..., description="The quiz question")
    options: List[Option] = Field(..., description="List of options for the question")
    correct_answer: str = Field(..., description="The correct answer's label")

class Quiz(BaseModel):
    quiz_title: str = Field(..., description="The title of the quiz")
    questions: List[Question] = Field(..., description="A list of quiz questions")


# Define the API tool for web searching using DuckDuckGo
search = DuckDuckGoSearchRun()

def get_web_summary(topic: str) -> str:
    """
    Searches the web for the given topic and returns a summary.
    Input should be a simple topic, like "quantum computing".
    """
    try:
        search_result = search.run(topic)
        return search_result
    except Exception as e:
        return f"An error occurred: {e}"

app = FastAPI(
    title="AI Microservice",
    description="A service to summarize text and generate quizzes using LangChain."
)

@app.get("/")
async def read_root():
    return {"message": "AI service is online!"}

# Endpoint for web-based summarization using LangChain Expression Language (LCEL)
@app.post("/summarize-web")
async def summarize_web(request: TopicRequest):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        template = """
        You are a helpful assistant that summarizes web search results.
        Summarize the following search result into a concise and easy-to-read paragraph.
        Search results: {search_result}
        """
        prompt = ChatPromptTemplate.from_template(template)
        search_and_summarize_chain = (
            RunnableParallel(
                search_result=lambda x: get_web_summary(x['topic'])
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        result = search_and_summarize_chain.invoke({"topic": request.topic})
        
        return {"summary": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for PDF summarization
@app.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")
    
    # Define the temporary file path
    temp_file_path = os.path.join("temp_uploads", file.filename)

    try:
        # Save the uploaded file to the temporary file
        os.makedirs("temp_uploads", exist_ok=True)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load the document using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        docs = loader.load_and_split()
        
       
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        
        prompt = ChatPromptTemplate.from_template("""
            Summarize the following document into a concise and easy-to-read paragraph.
            Document: {context}
        """)

        
        summarize_chain = create_stuff_documents_chain(llm, prompt)
        
        # Invoke the chain
        summary = await summarize_chain.ainvoke({"context": docs})
        
        
        os.remove(temp_file_path)
        
        return {"summary": summary}
    
    except Exception as e:
        # Clean up the temp file in case of an error
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Endpoint for combined summarization
@app.post("/summarize-combined")
async def summarize_combined(topic: str = Form(...), file: UploadFile = File(...)):
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are supported.")

    # Define the temporary file path
    pdf_path = os.path.join("temp_uploads", file.filename)

    try:
        # Create a temporary file for the PDF
        os.makedirs("temp_uploads", exist_ok=True)
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # Define the prompt for summarization
        prompt = ChatPromptTemplate.from_template("""
            Summarize the following documents from various sources into a single, cohesive, and easy-to-read paragraph.
            Documents: {context}
        """)

        
        summarize_chain = create_stuff_documents_chain(llm, prompt)

        # Use RunnableParallel to execute both loaders at the same time
        combined_loader_chain = RunnableParallel(
            web_docs=RunnablePassthrough.assign(
                page_content=lambda x: get_web_summary(x['topic'])
            ) | (lambda x: [Document(page_content=x['page_content'])]),
            pdf_docs=lambda x: PyPDFLoader(x['pdf_path']).load_and_split()
        )
        
        # Load the documents from both sources
        loaded_documents = await combined_loader_chain.ainvoke({"topic": topic, "pdf_path": pdf_path})

        
        all_documents = loaded_documents['web_docs'] + loaded_documents['pdf_docs']
        
        
        summary = await summarize_chain.ainvoke({"context": all_documents})
        
        # Clean up the temporary file
        os.remove(pdf_path)
        
        return {"summary": summary}
    
    except Exception as e:
        # Clean up in case of error
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Endpoint for quiz generation
@app.post("/generate-quiz", response_model=Quiz)
async def generate_quiz(request: QuizRequest):
    try:
        # Define the LLM (Gemini)
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

        # Create a structured output chain for the quiz
        structured_llm = llm.with_structured_output(Quiz)

        # Define the Prompt
        quiz_template = """
        You are a quiz-making expert. Given the following summary, create a multiple-choice quiz.
        The quiz should have at least 3 questions. Each question should have 3 options, and you must specify the correct option.
        You MUST follow the provided JSON schema for the output.

        Summary: {summary}
        """
        quiz_prompt = ChatPromptTemplate.from_template(quiz_template)

        
        quiz_chain = quiz_prompt | structured_llm

        
        quiz_data = await quiz_chain.ainvoke({"summary": request.summary})
        
        return quiz_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")