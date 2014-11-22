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
        mail = form.email.data.encode('ascii','ignore')
        mail = mail.lower()
        name = form.summoner_name.data.encode('ascii','ignore')
        name = name.lower()
        connect.cursor.execute("SELECT username FROM LEAGUE.USER WHERE username = '{0}'".format(mail))
        uniqueuser = connect.cursor.fetchall()
        connect.cursor.execute("SELECT sum_name FROM LEAGUE.USER WHERE sum_name = '{0}'".format(name))
        uniquename = connect.cursor.fetchall()
        if uniqueuser:
            print "user id taken"
            return redirect('sign-up')
            #need to put error message
        else:
            if uniquename:
                print "summoner name taken"
                return redirect('sign-up')
            else:
                if form.password.data.encode('ascii','ignore') == form.confirm.data.encode('ascii','ignore'):
                    connect.cursor.execute("INSERT INTO LEAGUE.USER VALUES ('{0}','{1}','{2}')".format(mail,form.password.data.encode('ascii','ignore'),name))
                    connect.conn.commit()
                    names = connect.cursor.execute("SELECT * FROM LEAGUE.USER WHERE username = '{0}'".format(mail))
                    print names
                    return redirect('home')
                else:
                    print "passwords don't match"
                    return redirect('sign-up')




    return render_template("signup.html", form=form)


@app.route('/home')
def home():
    return render_template("home.html")

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    class LogInForm(Form):
        email = StringField()
        password = PasswordField()

        def __str__(self):
            return  form.email.data

    form = LogInForm()
    if form.validate_on_submit():
        #print form.email.
        #qrrystr = "SELECT * FROM LEAGUE.USER WHERE username = (%s)", (form.email)# + form.email#connect.cursor.execute("SELECT * FROM LEAGUE.USER WHERE username = email()")
        value = form.email.data.encode('ascii','ignore')
        value = value.lower()
        print value
        connect.cursor.execute("SELECT * FROM LEAGUE.USER WHERE username = '{0}'" .format(value))
        records = connect.cursor.fetchall()
        password = form.password.data.encode('ascii','ignore')
        if records[0][1] == password:
            sumname = records[0][2]
            #valid session = true
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
    print "connecting to database\n ->%s" % (conn_string)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    #cursor.execute("SELECT Summoner_id FROM LEAGUE.PLAYER WHERE Summoner_id = 48445998")
    #records = cursor.fetchall()


if __name__ == '__main__':
    app.run(debug=True)


#if __name__ == "__main__":

#    main()