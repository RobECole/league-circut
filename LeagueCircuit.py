import psycopg2
import requests
from flask import Flask, render_template, redirect, flash, session, escape, request
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
        mail = form.email.data.encode('ascii', 'ignore')
        mail = mail.lower()
        name = form.summoner_name.data.encode('ascii', 'ignore')
        name = name.lower()
        connect.cursor.execute("SELECT username FROM LEAGUE.USER WHERE username = '{0}'".format(mail))
        err = 0
        if connect.cursor.fetchall():
            flash('User id already taken.')
            err = 1
            #return redirect('sign-up')
            #need to put error message
        connect.cursor.execute("SELECT sum_name FROM LEAGUE.USER WHERE sum_name = '{0}'".format(name))
        if connect.cursor.fetchall():
            flash('Summoner name already registered.')
            err = 1
            #return redirect('sign-up')
        if form.password.data.encode('ascii', 'ignore') != form.confirm.data.encode('ascii', 'ignore'):
            flash('Passwords do not match.')
            err = 1
        if err == 0:
            connect.cursor.execute("INSERT INTO LEAGUE.USER VALUES ('{0}','{1}','{2}')".format(mail, form.password.data.encode('ascii', 'ignore'), name))
            connect.conn.commit()
            redirect('log-in')
            return flash('Sign up successful!')
        else:
            return redirect('sign-up')
    return render_template("signup.html", form=form)


@app.route('/home')
def home():
    if 'username' in session:
        return render_template("home.html")
    return redirect("log-in"), flash('You are not logged in')


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    class LogInForm(Form):
        email = StringField()
        password = PasswordField()

        def __str__(self):
            return form.email.data

    form = LogInForm()
    if form.validate_on_submit():
        value = form.email.data.encode('ascii', 'ignore')
        value = value.lower()
        connect.cursor.execute("SELECT * FROM LEAGUE.USER WHERE username = '{0}'" .format(value))
        records = connect.cursor.fetchall()
        password = form.password.data.encode('ascii', 'ignore')
        if records:
            if records[0][1] == password:
                sumname = records[0][2]
                #valid session = true
                session['username'] = value
                print session['username']
                return redirect('home')
        else:
            #flash error
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

class connect():
    conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='RAMP'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

if __name__ == '__main__':
    app.run(debug=True)


#if __name__ == "__main__":

#    main()