from flask import Flask,render_template,request,jsonify,redirect,url_for
from auth import auth_bp,getCookieInfo
import memorai
import threading
from memorai import ask_model
from memorai import upload_experience,post
from imageai import get_caption
from pymongo import MongoClient
import json
from talk import text_to_speech
import os

app = Flask(__name__)
app.register_blueprint(auth_bp)

client = MongoClient(os.getenv("MONGO_URI"))
db=client["memory"]
collection = db["thoughts"]
user_collection = db["users"]
post_collection = db['community']

JSON_FILE_PATH = 'data.json'

def save_data(data):
    with open(JSON_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=4)

@app.route('/')
def home():
    token = request.cookies.get('cookie')
    if(token==None):
        print("check")
        return redirect(url_for("signin"))
    return render_template('index.html')
        

@app.route('/community')
def community():
    profiles = user_collection.find().to_list()
    arr=[]
    postarr=[]
    token = request.cookies.get("cookie")
    user_info = getCookieInfo(token)
    print(user_info)
    current_googleId = ""
    for profile in profiles:
        if(user_info[0]['sub']!=profile['sub']):
            arr.append({'sub':profile['sub'],'name':profile['name'],'picture':profile['picture'],'email':profile['email']})
        else:
            current_googleId=profile['sub']
    # print(arr)
    # save_data(jsonify({'data':profiles}))

    result= post_collection.find().sort("createdAt",-1).to_list()
    for post in result:
            for item in profiles:
                if post['googleId']==item['sub']:
                    postarr.append({'googleId':post['googleId'],'post':post['post'],'picture':item['picture'],'name':item['name']})
            
    print(postarr)

    return render_template('community.html',error=None,profiles=arr,postarr=postarr)



@app.route('/login')
def signin():
    return render_template('login.html',error = None)

@app.route('/recall')
def retrieve():

    return render_template('recall.html',response=None)

@app.route('/recallmemory',methods=['POST'])
def recall_():
    query = request.form['memory']
    token = request.cookies.get('cookie')
    user_info = getCookieInfo(token)
    if "/post" in query:
        memory=post(query,user_info[0]['sub'])
    else:    
        memory= ask_model(query,user_info[0]['sub'])
        threading.Thread(target=text_to_speech,args=(memory,)).start()
    return jsonify({'memory': memory})

# for updating the data base with new memory
@app.route('/update')
def update():
    return render_template('update.html',error = None)

@app.route('/updatememory',methods=['POST'])
def update_():
    token = request.cookies.get('cookie')
    user_info = getCookieInfo(token)
    file = request.files['file']
    if file:
        print("yes bro file present!!")
        if file.filename == '':
            return jsonify({"memory": "File is corrupted"})
        filepath = os.path.join("uploads", file.filename)
        file.save(filepath)
        caption = get_caption(filepath)
        caption = upload_experience(caption,user_info[0]['sub'])
        return jsonify({"memory": caption})
    else:
        exp = request.form['memory']
        print(user_info)
        exp= upload_experience(exp,user_info[0]['sub'])
        return jsonify({'memory': exp})


@app.route("/uploadimg", methods=[ "POST"])
def image_():
    if request.method == "POST":
        if 'file' not in request.files:
            return "No file uploaded", 400
        
    return render_template("index.html")




#768

if __name__ == '__main__':
    app.run(debug=True)
