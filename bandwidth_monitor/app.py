from flask import Flask, render_template, request,session,jsonify 
import urllib.request
from pusher import Pusher
from datetime import datetime
import httpagentparser
import json
import os
import hashlib
from dbsetup import create_connection, create_session,create_pages,update_or_create_page,select_all_sessions,select_all_pages,select_all_user_visits

#init the flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)

# configure pusher object
pusher = Pusher(
    app_id='1057374',
    key='3ecaba65a855b30d977a',
    secret='0c6740268a47044ca1f8',
    cluster='eu',
    ssl=True)

#connect to the db in the backend
database = "./pythonsqlite.db"
conn = create_connection(database)
c = conn.cursor()

#setting the col varibles to none
userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None

#init the main program func
def main():
     global conn, c

#parse the visitor data to the backend 
def parseVisitor(data):
    #establish pusher channels
    update_or_create_page(c, data)
    #pageview trigger 
    pusher.trigger(u'pageview', u'new', {
        u'page': data[0],
        u'session': sessionID,
        u'ip': userIP
    })
    #numbers trigger
    pusher.trigger(u'numbers', u'update', {
        u'page': data[0],
        u'session': sessionID,
        u'ip': userIP
    })

    #retrieves the data to pass to the backend
    @app.before_request
    def getAnalyticsData():
        #defining varibles that I want to find data about
        global userOS, userBrowser, userIP, userContinent, userCity, userCountry, sessionID
        #using httpagentparser to retrieve userOS & Browser 
        userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
        userOS = userInfo['platform']['name']
        userBrowser = userInfo['browser']['name']
        #api address which returns connection data
        api = "https://www.iplocate.io/api/lookup/" 
        try:
            #automate the browser to open the api address
            resp = urllib.request.urlopen(api)
            result = resp.read()
            #decode the json reponse to utf 
            result = json.loads(result.decode("utf-8"))
            #scraping the results for the rest of the params from the json blob
            userCountry = result["country"]
            userContinent = result["continent"]
            userCity = result["city"]
            userIP = result ["ip"]
        except:
            print("Could not find data ")
        getSession()

#
    def getSession():
        global sessionID
        time = datetime.now().replace(microsecond=0)
        if 'user' not in session:
            lines = (str(time)+userIP).encode('utf-8')
            session['user'] = hashlib.md5(lines).hexdigest()
            sessionID = session['user']
            pusher.trigger(u'session', u'new', {
                u'ip': userIP,
                u'continent': userContinent,
                u'country': userCountry,
                u'city': userCity,
                u'os': userOS,
                u'browser': userBrowser,
                u'session': sessionID,
                u'time': str(time),
            })
            data = [userIP, userContinent, userCountry,
                    userCity, userOS, userBrowser, sessionID, time]
            create_session(c, data)
        else:
            sessionID = session['user']

    @app.route('/')
    def index():
        data = ['home', sessionID, str(datetime.now().replace(microsecond=0))]
        parseVisitor(data)
        return render_template('index.html')

    @app.route('/about')
    def about():
        data = ['about', sessionID, str(datetime.now().replace(microsecond=0))]
        parseVisitor(data)
        return render_template('about.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/dashboard/<session_id>', methods=['GET'])
    def sessionPages(session_id):
        result = select_all_user_visits(c, session_id)
        return render_template("dashboard-single.html", data=result)

    @app.route('/get-all-sessions')
    def get_all_sessions():
        data = []
        dbRows = select_all_sessions(c)
        for row in dbRows:
            data.append({
                'ip': row['ip'],
                'continent': row['continent'],
                'country': row['country'],
                'city': row['city'],
                'os': row['os'],
                'browser': row['browser'],
                'session': row['session'],
                'time': row['created_at']
            })
        return jsonify(data)

    if __name__ == '__main__':
        app.run()
        
