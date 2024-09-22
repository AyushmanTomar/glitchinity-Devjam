import os
import pathlib
import requests
import jwt  # For JWT token generation
from datetime import datetime, timedelta
from flask import Flask, abort, redirect, request, jsonify, make_response,render_template, Blueprint
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from functools import wraps  # To preserve original function names
from dotenv import load_dotenv
from pymongo import MongoClient
import json
import pymongo
load_dotenv()

app = Flask("Google Login App")
app.secret_key = os.getenv("GOOGLE_CLIENT_SECRET")  # For JWT signing

client = MongoClient(os.getenv("MONGO_URI"))
db=client["memory"]
collection = db["thoughts"]
user_collection = db["users"]

auth_bp = Blueprint('auth',__name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # To allow HTTP traffic for local development

JWT_SECRET_KEY = "LAUDALASUN"  # Used for signing the JWT
# client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# Flow setup with credentials from environment variables (No client_secret.json)
flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [GOOGLE_REDIRECT_URI]
        }
    },
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",  # To access full profile including picture
        "https://www.googleapis.com/auth/userinfo.email",    # To access email
        "openid"
    ],
    redirect_uri=GOOGLE_REDIRECT_URI
)

# Helper function to generate JWT token
def generate_jwt(user_info):
    payload = {
        'sub': user_info['sub'],  # The user's Google ID
        'name': user_info['name'],
        'email': user_info['email'],
        'picture': user_info['picture'],  # Profile picture URL
        'exp': datetime.utcnow() + timedelta(minutes=30)  # JWT expiration time
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

# Middleware to verify JWT from cookies
def jwt_is_required(function):
    @wraps(function)  # Use wraps to preserve the original function name
    def wrapper(*args, **kwargs):
        token = request.cookies.get('cookie')
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        
        try:
            # Verify the token
            decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            request.user = decoded_token  # Store the user information from the token in the request object
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token!"}), 403
        
        return function(*args, **kwargs)
    
    return wrapper

def getCookieInfo(token):
    if not token:
        return {"error": "Missing token"}, 401
    
    try:
        # Decode the JWT using the secret key
        user_info = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        print(user_info)  # This will print the decoded user info
        return user_info, 200  # Return the decoded user info as a dictionary
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401


# Google OAuth login route
@auth_bp.route("/googleLogin")
def googleLogin():
    authorization_url, state = flow.authorization_url()
    return redirect(authorization_url)

# Google OAuth callback route
@auth_bp.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    # Verify and decode the token from Google
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    # Generate JWT token after successful login
    jwt_token = generate_jwt(id_info)

    check = user_collection.find_one({'sub':id_info['sub']})
    print(check)
    if(check==None):
       user_collection.insert_one(id_info)
    # Set JWT token in cookies
    response = make_response(redirect("/"))
    # response = make_response(redirect("/protected_area"))
    # response.set_cookie("cookie", jwt_token, httponly=True) #Use this once website out for production
    response.set_cookie('cookie',jwt_token, max_age=60 * 60 * 24 * 7)
    return response

# Logout route
@auth_bp.route("/logout")
def logout():
    response = make_response(redirect("/"))
    response.delete_cookie('cookie')
    return response

# Protected area (JWT token required)
@auth_bp.route("/protected_area")
@jwt_is_required
def protected_area():
    # Access user info from JWT token stored in cookies
    user_info = request.user
    print(user_info)
    return f"""
    <h1>Hello {user_info['name']}!</h1>
    <p>Email: {user_info['email']}</p>
    <img src="{user_info['picture']}" alt="Profile Picture" style="width:100px; height:100px;"><br/>
    <a href='/logout'><button>Logout</button></a>
    """

# Route to check if JWT token is valid
@auth_bp.route("/check_jwt_token")
@jwt_is_required
def check_jwt_token():
    return jsonify({"message": "JWT token is valid!"})

@auth_bp.route("/printToken")
@jwt_is_required
def printToken():
    token = request.cookies.get('cookie')
    print(token)
    return getCookieInfo(token)



if __name__ == "__main__":
    app.run(debug=True)
