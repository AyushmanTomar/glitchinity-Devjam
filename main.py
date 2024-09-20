import pymongo
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import requests
import json

# mongo db details
client = MongoClient("your_mongodb_atlas_connection_string")
db = client["your_database_name"]
collection = db["your_collection_name"]


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

def search_similar_documents(query, k=5):
    # Create query embedding
    query_embedding = e_model.encode(query)
    
    # Search for similar documents
    results = collection.aggregate([
        {
            "$search": {
                "index": "default",
                "knnBeta": {
                    "vector": query_embedding.tolist(),
                    "path": "embedding",
                    "k": k
                }
            }
        }
    ])
    
    return [doc["text"] for doc in results]


def get_response_to_post(input_text):
    prompt=ChatPromptTemplate.from_messages(
        [
            ("system","You are a helpful assistant. Please response to the user queries"),
            ("user","Question:{question}")
        ]
    )
    llm=Ollama(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    return(chain.invoke({"question":input_text}))


input_text="what is factorial of 3?"
