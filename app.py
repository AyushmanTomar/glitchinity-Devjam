from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def signin():
    return render_template('login.html',error = None)

@app.route('/recall')
def retrieve():
    return render_template('recall.html',response=None)

@app.route('/update')
def update():
    return render_template('update.html',error = None)

#768

if __name__ == '__main__':
    app.run(debug=True)
