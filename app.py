from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def signin():
    return render_template('login.html')

@app.route('/recall')
def retrieve():
    return render_template('recall.html')

if __name__ == '__main__':
    app.run(debug=True)
