from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sign-up')
def sign_up():
    return render_template("signup.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/log-in')
def log_in():
    return  render_template("login.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True)
