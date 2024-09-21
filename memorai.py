import pymongo
import os 
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# mongo db details
client = MongoClient(os.getenv("MONGO_URI"))
db=client["memory"]
collection = db["thoughts"]


e_model = SentenceTransformer('all-mpnet-base-v2')#all-MiniLM-L6-v2

def create_embedding(text):
    embedding = e_model.encode(text)
    return embedding

def add_to_database(context):
    doc = {
        "context":context,
        "embedding":create_embedding(context).tolist(),
        "createdAt":datetime.utcnow()
    }
    result = collection.insert_one(doc)


def search_similar_documents(query):
    results = collection.aggregate([
        {"$vectorSearch":{
            "queryVector":create_embedding(query).tolist(),
            "path":"embedding",
            "numCandidates":300,
            "limit":2,
            "index":"default"
        }}
    ])
    
    return [doc["context"] for doc in results]

def create_context(experience):
    prompt=ChatPromptTemplate.from_messages(
        [
            ("system","""You are an intelligent assistant designed to help users manage their experiences, reminders, and events. Your task is to generate concise and contextually relevant summaries based on the user's input. Consider the type of input (experience, reminder, event,general) and the time provided by the user. Ensure the summary is personalized and includes any relevant details that would help the user recall the event or reminder in the future.\n\nInstructions:\n1. Identify the type of input .\n2. Extract key details from the user's input, including the time and date.\n3. Generate a concise summary that includes the main points and any relevant context.\n4. Ensure the summary is clear, informative, and personalized to the user's needs.\n\nExamples:\n1. User Input: "I have a quiz on Monday at 10 AM."\nSummary: "Reminder: You have a quiz scheduled for Monday at 10 AM."\n\n2. User Input: "I went to the beach with friends last Saturday. We had a great time swimming and playing volleyball."\nSummary: "Experience: Last Saturday, you enjoyed a beach day with friends, swimming and playing volleyball."\n\n3. User Input: "Doctor's appointment on September 25th at 3 PM."\nSummary: "Reminder: You have a doctor's appointment on September 25th at 3 PM."\n\nRemember to always include the time and date if provided, and tailor the summary to be as helpful and relevant as possible for the user."""),
            ("user","{experience} generate contex summary to store in database")
        ]
    )
    llm2=Ollama(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|llm2|output_parser
    return(chain.invoke({"experience":experience}))



def get_response_to_post(input_text,query):
    text=""
    for context in input_text:
        text=text+context

    prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user's queries with reference to the context. If the context is not found, handle it with an appropriate output. Describe the situation in good words and ending with a follow up question to assist further or a giving a greeting or asking more about the happened event."),
        ("user", "Context: {context}\n\nQuestion: {query}\n\nAnswer: Based on the your memory provided, here is what i found:")
    ]
    )
    llm=Ollama(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    return(chain.invoke({"context": text, "query": query}))



def ask_model(query):
    input_text=search_similar_documents(query)
    return(get_response_to_post(input_text,query))

def upload_experience(experience):
    experience=create_context(experience)
    print(experience)
    add_to_database(experience)

# upload_experience("i am sitting in a hackathon at 3pm on 21 september 2024. i am really tired dont know what to do")