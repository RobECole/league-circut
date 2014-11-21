import psycopg2
import sys
import pprint
from flask import Flask, render_template, redirect, flash
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    class SignUpForm(Form):
        email = StringField()
        password = PasswordField()
        confirm = PasswordField()
        summoner_name = StringField()

    form = SignUpForm()
    if form.validate_on_submit():
        flash("success")
        # Call some function to check if new
        # IF NOT UNIQUE FLASH ERROR
        # else get summoners ID
        return redirect('home')


    return render_template("signup.html", form=form)


@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    class LogInForm(Form):
        email = StringField()
        password = PasswordField()

    form = LogInForm()
    if form.validate_on_submit():
        connect.cursor.execute("SELECT * FROM LEAGUE.USER WHERE EMAIL = email")
        records =connect.cursor.fetchaall()
        print records
    return render_template("login.html", form=form)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    app.run(debug=True)

class connect():
    conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='RAMP'"
    print "connecting to database\n ->%s" % (conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    #cursor.execute("SELECT Summoner_id FROM LEAGUE.PLAYER WHERE Summoner_id = 48445998")
    #records = cursor.fetchall()

#if __name__ == "__main__":

#    main()