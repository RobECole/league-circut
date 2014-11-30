import psycopg2
from flask import Flask, render_template, redirect, flash, session
import requests
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
import riotwatcher
import atexit


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
key = '1dbf97cc-5028-4196-a05c-6645adc80bef'
w = riotwatcher.RiotWatcher(key)
FlaskService = 'http://127.0.0.1:5001/api/'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/sign-out')
def sign_out():
    if 'username' in session:
        del session['username']
    return redirect('/')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    class SignUpForm(Form):
        email = StringField()
        password = PasswordField()
        confirm = PasswordField()
        summoner_name = StringField()
    form = SignUpForm()
    if form.validate_on_submit():
        mail = form.email.data.encode('ascii', 'ignore').lower()
        name = form.summoner_name.data.encode('ascii', 'ignore').lower()
        connect.cursor.execute("SELECT username FROM LEAGUE.USER WHERE username = '{0}'".format(mail))
        err = False
        if connect.cursor.fetchall():
            flash('User id already taken.')
            err = True
            #return redirect('sign-up')
            #need to put error message
        connect.cursor.execute("SELECT sum_name FROM LEAGUE.USER WHERE sum_name = '{0}'".format(name))
        if connect.cursor.fetchall():
            flash('Summoner name already registered.')
            err = True
            #return redirect('sign-up')
        if form.password.data.encode('ascii', 'ignore') != form.confirm.data.encode('ascii', 'ignore'):
            flash('Passwords do not match.')
            err = True
        if not err:
            connect.cursor.execute("INSERT INTO LEAGUE.USER VALUES ('{0}','{1}','{2}')".format(mail, form.password.data.encode('ascii', 'ignore'), name))
            connect.conn.commit()
            return redirect('log-in')
        else:
            return redirect('sign-up')
    return render_template("signup.html", form=form)


@app.route('/home', methods=['GET','POST'])
def home():
   #if 'username' in session:


   free = requests.get(FlaskService + 'freeChamps').json()
   print free
   return render_template("home.html")


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
                id = summoner['id']
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
                mId = '1612909742'
                match = w.get_match(mId)
                #print match
                player = match.get('participants')

                playerid = match.get('participantIdentities')
                msumid = []
                msumname = []
                cid = []
                tid = []
                win = []
                clevel = []
                kills = []
                deaths = []
                assists = []
                cs = []
                partid = []
                goldearned = []
                damagedealt = []
                mType = match.get('queueType')
                mDuration = match.get('matchDuration')
                length = len(player)
                for x in xrange(length):
                    playerids = playerid[x].get('player')
                    if playerid:
                        msumid.append(playerids.get('summonerId'))
                        msumname.append(playerids.get('summonerName'))
                        msumname[x] = msumname[x].encode('ascii', 'ignore')
                    else:
                        msumid.append(x+1)
                        msumname.append(x+1)
                    cid.append(player[x].get('championId'))
                    tid.append(player[x].get('teamId'))
                    partid.append(player[x].get('participantId'))
                    pstats = player[x].get('stats')
                    win.append(pstats.get('winner'))
                    clevel.append(pstats.get('champLevel'))
                    kills.append(pstats.get('kills'))
                    deaths.append(pstats.get('deaths'))
                    assists.append(pstats.get('assists'))
                    cs.append(pstats.get('minionsKilled'))
                    goldearned.append(pstats.get('goldEarned'))
                    damagedealt.append(pstats.get('totalDamageDealtToChampions'))
                for x in xrange(length):
                    connect.cursor.execute("UPDATE LEAGUE.MATCH SET champion_id = '{0}', team_id = '{1}', game_type = '{2}', winner = '{3}', duration = '{4}' WHERE match_id = '{5}' AND summoner_id = '{6}'".format(cid[x], tid[x], mType, win[x], mDuration, mId, msumid[x]))
                    if connect.cursor.rowcount == 0:
                        connect.cursor.execute("INSERT INTO LEAGUE.MATCH VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(msumid[x], mId, cid[x], tid[x], mType, win[x], mDuration))

                    connect.cursor.execute("UPDATE LEAGUE.MATCH_STATS SET champion_id = '{0}', champlevel = '{1}', kills = '{2}', deaths = '{3}', assists = '{4}', creep_kills = '{5}', gold_earned = '{6}', damage_dealt_to_champs = '{7}' WHERE match_id = '{8}' AND participant_id = '{9}'".format(cid[x], clevel[x], kills[x], deaths[x], assists[x], cs[x], goldearned[x], damagedealt[x], mId, partid[x]))
                    if connect.cursor.rowcount == 0:
                        connect.cursor.execute("INSERT INTO LEAGUE.MATCH_STATS VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(cid[x], clevel[x], kills[x], deaths[x], assists[x], cs[x], goldearned[x], damagedealt[x], mId, msumid[x]))

                    connect.cursor.execute("UPDATE LEAGUE.PLAYER SET summoner_id = '{0}', player_level = '{1}', game_id = '{2}', team_id = '{3}', unranked_win = '{4}', ranked_win3v3 = '{5}', ranked_win5v5 = '{6}' WHERE summoner_name = '{7}'".format(id, level, match_id, team_id, unranked, win3v3, win5v5, sumname))
                    if connect.cursor.rowcount == 0:
                        connect.cursor.execute("INSERT INTO LEAGUE.PLAYER VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')".format(id, sumname, level, match_id, team_id, unranked, win3v3, win5v5))
                    connect.conn.commit()


                session['username'] = sumname
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
    conn_string = "host='localhost' dbname='LEAGUE_CIRCUIT' user='postgres' password='testdb'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

def exit_handler():
    print "Application ending"

atexit.register(exit_handler)

if __name__ == '__main__':
    app.run(debug=True)



#if __name__ == "__main__":

#    main()
#How to fill Table Champion
#champname = "insert champ name here"
#try:
    #champid = connect.cursor.execute("SELECT id FROM LEAGUE.CHAMPNAME WHERE name = champname")
    #champion = w.get_champion(champid)
    #rankedPlayEnable = champion.get('rankedPlayEnabled')
    #botEnabled = champion.get('botEnabled')
    #freeToPlay = champion.get('freeToPlay')
#except:
    #print "Invalid champion id"

#How to fill Table Match
#match = w.get_match('1647417800')
#get sumid sumid = match.get
#get matchid
#get champid
#get teamid
#get gametype
#get winner
#get length
