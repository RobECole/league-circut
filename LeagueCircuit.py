import psycopg2
from flask import Flask, render_template, redirect, flash, session
import requests
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField
import riotwatcher
import atexit


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.service = 'http://127.0.0.1:5001/api/'
key = '1dbf97cc-5028-4196-a05c-6645adc80bef'
w = riotwatcher.RiotWatcher(key)


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
        #print
        try:
            w.get_summoner(name)
        except:
            flash("Invalid summoner name.  Please enter a valid summoner name", 'signup')
            err = True
        if connect.cursor.fetchall():
            flash('User id already taken.', 'signup')
            err = True
            #return redirect('sign-up')
            #need to put error message
        connect.cursor.execute("SELECT sum_name FROM LEAGUE.USER WHERE sum_name = '{0}'".format(name))
        if connect.cursor.fetchall():
            flash('Summoner name already registered.', 'signup')
            err = True
            #return redirect('sign-up')
        if form.password.data.encode('ascii', 'ignore') != form.confirm.data.encode('ascii', 'ignore'):
            flash('Passwords do not match.', 'signup')
            err = True
        if not err:
            connect.cursor.execute("INSERT INTO LEAGUE.USER VALUES ('{0}','{2}','{1}')".format(mail, form.password.data.encode('ascii', 'ignore'), name))
            connect.conn.commit()
            return redirect('log-in')
        else:
            return redirect('sign-up')
    return render_template("signup.html", form=form)


@app.route('/home', methods=['GET', 'POST'])
def home():
    #if 'username' in session:
    #connect.cursor.execute("SELECT summoner_id, game_id FROM LEAGUE.PLAYER WHERE summoner_name = '{0}'".format(session['username']))
    #passing = connect.cursor.fetchall()
    topkills = requests.get(app.service + 'topkills/' + str(match_id)).json()['top']
    lastgame = requests.get(app.service + 'lastGame/' + str(id)).json()['last']
    freechamps = requests.get(app.service + 'freeChamps').json()['data']
    fastgame = requests.get(app.service + 'fastgame/' + str(id)).json()['fast']
    return render_template("home.html", summoner=session['username'], data=freechamps, last=lastgame, top=topkills, fast=fastgame)



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
        #champupdate()
        if records:
            print "loginpart1"
            if records[0][2] == password:
                print "loginpart2"
                sumname = records[0][1]
                summoner = w.get_summoner(sumname)
                global id
                global match_id
                id = summoner['id']
                newid = id
                print id
                try:
                    match_history = w.get_recent_games(id)
                    match_history = match_history.get('games')
                    checkteam =  match_history[0].get('stats').get('team')
                    checkchamp = match_history[0].get('championId')
                    for x in range(0, len(match_history)):
                        match_id = match_history[x].get('gameId')
                        connect.cursor.execute("UPDATE LEAGUE.MATCHLIST SET sumid = '{0}' WHERE id = '{1}'".format(id, match_id))
                        if connect.cursor.rowcount == 0:
                                connect.cursor.execute("INSERT INTO LEAGUE.MATCHLIST VALUES ('{0}', '{1}')".format(id, match_id))
                    match_id = match_history[0].get('gameId')
                except:
                    print 'No match history found'
                    match_id = 0
                try:
                    team = w.get_teams_for_summoner(id)
                    for x in range(0, len(team)):
                        teamid = team[x].get('fullId')
                        connect.cursor.execute("UPDATE LEAGUE.TEAMLIST SET sumid = '{0}' WHERE id = '{1}'".format(id, teamid))
                        if connect.cursor.rowcount == 0:
                            connect.cursor.execute("INSERT INTO LEAGUE.TEAMLIST VALUES('{0}', '{1}')".format(id, teamid))
                    teamid = team[1].get('fullId')
                    teamstat = team[0].get('teamStatDetails')
                    win5v5 = teamstat[0].get('wins')
                    win3v3 = teamstat[1].get('wins')
                    team_record = w.get_team(teamid)
                    tname = team_record.get('name')
                    tname = tname.encode('ascii', 'ignore')
                    team_record = team_record.get('teamStatDetails')
                    for x in range(0, len(team_record)):
                        if team_record[x].get('teamStatType') == 'RANKED_TEAM_3x3':
                            twin3v3 = team_record[x].get('wins')
                            tloss3v3 = team_record[x].get('losses')
                        elif team_record[x].get('teamStatType') == 'RANKED_TEAM_5x5':
                            twin5v5 = team_record[x].get('wins')
                            tloss5v5 = team_record[x].get('losses')
                except:
                    print 'No team data found'
                    teamid = 0
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

                try:
                    match = w.get_match(match_id)
                    match_found = True
                except:
                    match_found = False
                level = summoner.get('summonerLevel')
                mId = match_id
                #print match
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
                if match_found == True:
                    for x in xrange(len(match_history)):
                        print len(match_history)
                        mId = match_history[x].get('gameId')
                        mDuration = match_history[x].get('stats').get('timePlayed')
                        connect.cursor.execute("UPDATE LEAGUE.MATCH SET duration = '{0}' WHERE match_id = '{1}' AND summoner_id = '{2}'".format(mDuration, mId, id))
                        if connect.cursor.rowcount == 0:
                            connect.cursor.execute("INSERT INTO LEAGUE.MATCH VALUES ('{0}','{1}',0,0,0,0,True, '{2}')".format(id, mId, mDuration))
                    mId = match_id
                    player = match.get('participants')
                    playerid = match.get('participantIdentities')
                    mType = match.get('queueType')
                    mDuration = match.get('matchDuration')
                    #mDuration = "{0}:{1}".format(mDuration / 60, mDuration % 60)
                    length = len(player)
                    for x in xrange(length):
                        playerids = playerid[x].get('player')
                        if playerids:
                            msumid.append(playerids.get('summonerId'))
                            msumname.append(playerids.get('summonerName'))
                            msumname[x] = msumname[x].encode('ascii', 'ignore')
                        else:
                            msumid.append(x+1)
                            msumname.append(x+1)
                        cid.append(player[x].get('championId'))
                        tid.append(player[x].get('teamId'))
                        if cid[x] == checkchamp and tid[x] == checkteam:
                            msumid[x] = id
                            msumname[x] = sumname
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
                        connect.cursor.execute("UPDATE LEAGUE.MATCH SET champion_id = '{0}', participant_id = '{1}', team_id = '{2}', game_type = '{3}', winner = '{4}', duration = '{5}' WHERE match_id = '{6}' AND summoner_id = '{7}'".format(cid[x], partid[x], tid[x], mType, win[x], mDuration, mId, msumid[x]))
                        if connect.cursor.rowcount == 0:
                            connect.cursor.execute("INSERT INTO LEAGUE.MATCH VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}', '{7}')".format(msumid[x], mId, cid[x], partid[x], tid[x], mType, win[x], mDuration))

                        connect.cursor.execute("UPDATE LEAGUE.MATCH_STATS SET champion_id = '{0}', champlevel = '{1}', kills = '{2}', deaths = '{3}', assists = '{4}', creep_kills = '{5}', gold_earned = '{6}', damage_dealt_to_champs = '{7}' WHERE match_id = '{8}' AND participant_id = '{9}'".format(cid[x], clevel[x], kills[x], deaths[x], assists[x], cs[x], goldearned[x], damagedealt[x], mId, partid[x]))
                        if connect.cursor.rowcount == 0:
                            connect.cursor.execute("INSERT INTO LEAGUE.MATCH_STATS VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(mId, partid[x], cid[x], clevel[x], kills[x], deaths[x], assists[x], cs[x], goldearned[x], damagedealt[x]))

                    connect.cursor.execute("UPDATE LEAGUE.PLAYER SET summoner_id = '{0}', player_level = '{1}', game_id = '{2}', team_id = '{3}', unranked_win = '{4}', ranked_win3v3 = '{5}', ranked_win5v5 = '{6}' WHERE summoner_name = '{7}'".format(id, level, match_id, teamid, unranked, win3v3, win5v5, sumname))
                    if teamid != 0:
                        connect.cursor.execute("UPDATE LEAGUE.TEAM SET team_name = '{0}', wins3v3 = '{1}', losses3v3 = '{2}', wins5v5 = '{3}', losses5v5 = '{4}' WHERE team_id = '{5}'".format(tname, twin3v3, tloss3v3, twin5v5, tloss5v5, teamid))
                        if connect.cursor.rowcount == 0:
                            connect.cursor.execute("INSERT INTO LEAGUE.TEAM VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')".format(teamid, tname, twin3v3, tloss3v3, twin5v5, tloss5v5))
                    connect.cursor.execute("UPDATE LEAGUE.PLAYER SET summoner_id = '{0}', player_level = '{1}', game_id = '{2}', team_id = '{3}', unranked_win = '{4}', ranked_win3v3 = '{5}', ranked_win5v5 = '{6}' WHERE summoner_name = '{7}'".format(id, level, match_id, teamid, unranked, win3v3, win5v5, sumname))
                    if connect.cursor.rowcount == 0:
                        connect.cursor.execute("INSERT INTO LEAGUE.PLAYER VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}')".format(id, sumname, level, match_id, teamid, unranked, win3v3, win5v5))
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

class champupdate():
    champions = w.get_all_champions()
    champions = champions.get('champions')
    c1 = []
    c2 = []
    c3 = []
    c4 = []
    for x in xrange(len(champions)):
        c = champions[x]
        c1.append(c.get('id'))
        c2.append(c.get('rankedPlayEnabled'))
        c3.append(c.get('botEnabled'))
        c4.append(c.get('freeToPlay'))
        connect.cursor.execute("UPDATE LEAGUE.CHAMPION SET ranked_play_enabled = '{0}', bot_enabled = '{1}', free_to_play = '{2}' WHERE champ_id = '{3}'".format(c2[x], c3[x], c4[x], c1[x]))
        if connect.cursor.rowcount == 0:
            connect.cursor.execute("INSERT INTO LEAGUE.CHAMPION VALUES ('{0}','{1}','{2}','{3}')".format(c1[x], c2[x], c3[x], c4[x]))
    connect.conn.commit()




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
