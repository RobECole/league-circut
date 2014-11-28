import psycopg2
import sys
from os import path
from flask import Flask, render_template, redirect, flash, session, escape, request
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
import riotwatcher
import atexit
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
key = '1dbf97cc-5028-4196-a05c-6645adc80bef'
w = riotwatcher.RiotWatcher(key)
print(w.can_make_request())
@app.route('/')
def index():
    try:
        del session['username']
    except:
        pass
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
            return redirect('log-in')
        else:
            return redirect('sign-up')
    return render_template("signup.html", form=form)


@app.route('/home')
def home():
    if 'username' in session:
        print session
        #get the last game from web service
        return render_template("home.html")
    flash('You are not logged in')
    return redirect("log-in")



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
                summoner = w.get_summoner(sumname)
                id = summoner.get('id')
                try:
                    match_history = w.get_match_history(id)
                    match_id = match_history.get('matches')
                    match_id = match_id[0].get('matchId')
                except:
                    print 'No match history found'
                    match_id = 0
                try:
                    team = w.get_teams_for_summoner(id)
                    team_id = team[1].get('fullId')
                    teamstat = team[0].get('teamStatDetails')
                    win5v5 = teamstat[0].get('wins')
                    win3v3 = teamstat[1].get('wins')
                except:
                    print 'No team data found'
                    team_id = 0
                    win5v5 = 0
                    win3v3 = 0
                try:
                    stat = w.get_stat_summary(id)
                    unranked = stat.get('playerStatSummaries')
                    for x in range(0, len(unranked)-1):
                        k = unranked[x].get('playerStatSummaryType')
                        if k == 'Unranked':
                            unranked = unranked[x].get('wins')
                            break
                except:
                    print 'No stats found'
                    unranked = 0
                level = summoner.get('summonerLevel')
                connect.cursor.execute("INSERT INTO LEAGUE.PLAYER VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')".format(id, sumname, level, match_id, team_id, unranked, win3v3, win5v5))
                connect.conn.commit()
                session['username'] = value
                print session['username']
                return redirect('home')
        else:
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

class connect():
    conn_string = "host='localhost' dbname='league_circuit' user='postgres' password='testdb'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

def exit_handler():
    print "Application ending"

atexit.register(exit_handler)

if __name__ == '__main__':
    app.run(debug=True)



#if __name__ == "__main__":

#    main()