import os 
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# mongo db details
client = MongoClient(os.getenv("MONGO_URI"))
db=client["memory"]
collection = db["thoughts"]
post_collection = db['community']


e_model = SentenceTransformer('all-mpnet-base-v2')#all-MiniLM-L6-v2

def create_embedding(text):
    embedding = e_model.encode(text)
    return embedding

def add_to_database(context,googleId):
    doc = {
        "googleId":googleId,
        "context":context,
        "embedding":create_embedding(context).tolist(),
        "createdAt":datetime.utcnow()
    }
    result = collection.insert_one(doc)


def search_similar_documents(query,googleId):
    results = collection.aggregate([
        # Atlas Search stage (without filter)
        {
            "$search": {
                "index": "default",  # Your Atlas Search index name
                "knnBeta": {
                    "vector": create_embedding(query).tolist(),
                    "path": "embedding",
                    "k": 300  # Number of candidates
                }
            }
        },
        {
            "$match": {
                "googleId": googleId
            }
        },
        {"$limit": 3}
    ])


    
    return [doc["context"] for doc in results]

def create_context(experience):
    prompt=ChatPromptTemplate.from_messages(
        [
            ("system","""You are a helpful assistant, but not allowed to print anything extra except what is asked
             Generate contextual summary from user's perspective. keep it raw and form first person sentences to include all details.
             Remember you are not allowed to print any extra informaion, just the contextual summary."""),
            ("user","{experience} generate context summary to store in database")
        ]
    )
    llm2=Ollama(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|llm2|output_parser
    return(chain.invoke({"experience":experience}))

def post(query,googleId):
    arr=search_similar_documents(query,googleId)
    text=""
    i=1
    for context in arr:
        text=text+"context"+str(i)+"-"+context+"\n"
        i+=1
    prompt=ChatPromptTemplate.from_messages(
        [
            ("system","""You are a helpful assistant to post on social media,
             Generate contextual summary from user's perspective. keep it raw and form first person sentences to include all details.
             Make it catchy and generate post text based on context given,Remember you are not allowed to print any extra informaion. Do not give any introduction and conclusion and headings to generated output"""),
            ("user","{experience} give me a single descriptive text to post,Remember you are not allowed to print any extra informaion ")
        ]
    )
    llm2=Ollama(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|llm2|output_parser
    text=chain.invoke({"experience":text})
    print(text)
    doc = {
        'googleId':googleId,
        'post':text,
        'createdAt':datetime.utcnow()
    }
    result = post_collection.insert_one(doc)
    return text






def get_response_to_post(input_text,query):
    text=""
    i=1
    for context in input_text:
        text=text+"context"+str(i)+"-"+context+"\n"
        i+=1
    prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user's queries with reference to the context.Select the most relevant context and answer the question. If the related context is not found, handle it with an appropriate output. Describe the situation in good words and ending with a follow up question to assist further or a giving a greeting or asking more about the happened event.You must not print context. Do not answer any other query related to coding or any other stuff"),
        ("user", "Context: {context}\n\nQuestion: {query}\n\nBased on the your memory provided, here is what i found:")
    ]
    )
    llm=Ollama(model="llama3.1")
    output_parser=StrOutputParser()
    chain=prompt|llm|output_parser
    return(chain.invoke({"context": text, "query": query}))



def ask_model(query,googleId):
    input_text=search_similar_documents(query,googleId)
    return(get_response_to_post(input_text,query))

def upload_experience(experience,googleId):
    experience=create_context(experience)
    print(experience)
    add_to_database(experience,googleId)
    return("Experinece added!!")



# upload_experience("my aunt scolded me tonight i felt very bad about it. i am nit hapy")
