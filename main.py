import pymongo
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import requests
import json

#mongo db details
# client = MongoClient("your_mongodb_atlas_connection_string")
# db = client["your_database_name"]
# collection = db["your_collection_name"]


e_model = SentenceTransformer('all-mpnet-base-v2')#all-MiniLM-L6-v2

def create_embedding(text):
    embedding = e_model.encode(text)
    return embedding
    

def add_to_database(text):
    embedding = e_model.encode(text)
    
    doc = {
        "text": text,
        "embedding": embedding.tolist()
    }
    collection.insert_one(doc)

from langchain_ollama import OllamaLLM

# Initialize the Llama 3.1 model
llm = OllamaLLM(model="llama3.1")

# Invoke the model with a prompt
response = llm.invoke("The first man on the moon was ...")

# Print the response
print(response)
