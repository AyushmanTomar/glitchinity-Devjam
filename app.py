from flask import Flask,render_template,request,jsonify
from auth import auth_bp
import memorai
from memorai import ask_model
from memorai import upload_experience
app = Flask(__name__)
app.register_blueprint(auth_bp)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def signin():
    return render_template('login.html',error = None)

@app.route('/recall')
def retrieve():
    return render_template('recall.html',response=None)

@app.route('/recallmemory',methods=['POST'])
def recall_():
    query = request.form['memory']
    memory= ask_model(query)
    return jsonify({'memory': memory})

# for updating the data base with new memory
@app.route('/update')
def update():
    return render_template('update.html',error = None)

@app.route('/updatememory',methods=['POST'])
def update_():
    exp = request.form['memory']
    exp= upload_experience(exp)
    return jsonify({'memory': exp})



#768

if __name__ == '__main__':
    app.run(debug=True)
