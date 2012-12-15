import socket
from flask import Flask, request, url_for, flash, session, redirect
from flask.ext.login import LoginManager, login_user
from flask.ext.pymongo import PyMongo
from flask_oauth import OAuth, OAuthException
import json
from bson import json_util
import os
from User import User


_is_deploy = True
if socket.gethostname() in ['au01rh00122','SteMac.local']: _is_deploy = False


app = Flask(__name__)
if _is_deploy:
    app.config['MONGO_HOST'] = os.environ['OPENSHIFT_MONGODB_DB_HOST']
    app.config['MONGO_USERNAME'] = os.environ['OPENSHIFT_MONGODB_DB_USERNAME']
    app.config['MONGO_PASSWORD'] = os.environ['OPENSHIFT_MONGODB_DB_PASSWORD']
    app.config['MONGO_DBNAME'] = os.environ['OPENSHIFT_APP_NAME']
else:
    app.config['MONGO_URI'] = 'mongodb://localhost/watchit'

oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='4TTmTkkoDqUuxsDhKYzXQ',
    consumer_secret='nebfZIBjCa8VnKxkf2KVe76EjtFbEalGr5DPqa7YU9A'
)

app.secret_key = 'A0Zr98j/3yX R~XH()!jmN]LWX/,?RTSTEVENMM'

login_manager = LoginManager()
login_manager.init_app(app)

#mongo = PyMongo(app)

@app.route('/')
def home_page():
#    try:
#        print mongo.db.openshift.find_one()
#    except Exception, e:
#        print e
#    o = twitter.get('statuses/show/')
    if session.get('twitter_user'):
        return 'hello'+ session.get('twitter_user')
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next=request.args.get('next') or request.referrer or None))

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    # http://packages.python.org/Flask-OAuth/
    next_url = request.args.get('next') or url_for('home_page')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
        )
    session['twitter_user'] = resp['screen_name']

    flash('You were signed in as %s' % resp['screen_name'])
    user = User(resp['screen_name'],resp['screen_name'])

    # http://packages.python.org/Flask-Login/
    login_user(user)
    return redirect(next_url)


@app.errorhandler(OAuthException)
def handle_oauth_exception(error):
    return 'OAuthException, please try later.'


if __name__ == '__main__':

    app.run(debug=True)