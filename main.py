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


# def get_response_to_post(input_text):
#     prompt=ChatPromptTemplate.from_messages(
#         [
#             ("system","You are a helpful assistant. Please response to the user queries"),
#             ("user","Question:{question}")
#         ]
#     )
#     llm=Ollama(model="llama3.1")
#     output_parser=StrOutputParser()
#     chain=prompt|llm|output_parser
#     return(chain.invoke({"question":input_text}))


# input_text="what is factorial of 3?"

query = "dog"
print(search_similar_documents(query))
# add_to_database(query)
# add_to_database();
