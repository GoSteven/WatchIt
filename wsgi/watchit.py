import socket
from flask import Flask, request, url_for, flash, session, redirect, render_template
from flask.ext.login import LoginManager, login_user, current_user, login_required, logout_user
from flask.ext.mongoalchemy import MongoAlchemy
from flask_oauth import OAuth, OAuthException
import json
from bson import json_util
import os

SECRET_KEY = 'A0Zr98j/3yX R~XH()!jmN]LWX/,?RTSTEVENMM'
FACEBOOK_APP_ID = '339967149444676'
FACEBOOK_APP_SECRET = 'aa7cafd863dc9533f42a3d9c31f6b802'
TWITTER_APP_ID = '4TTmTkkoDqUuxsDhKYzXQ'
TWITTER_APP_SECRET = 'nebfZIBjCa8VnKxkf2KVe76EjtFbEalGr5DPqa7YU9A'


_is_deploy = True
if socket.gethostname() in ['au01rh00122','SteMac.local']: _is_deploy = False


app = Flask(__name__)
if _is_deploy:
    app.config['MONGOALCHEMY_SERVER'] = os.environ['OPENSHIFT_MONGODB_DB_HOST']
    app.config['MONGOALCHEMY_USER'] = os.environ['OPENSHIFT_MONGODB_DB_USERNAME']
    app.config['MONGOALCHEMY_PASSWORD'] = os.environ['OPENSHIFT_MONGODB_DB_PASSWORD']
    app.config['MONGOALCHEMY_DATABASE'] = os.environ['OPENSHIFT_APP_NAME']
else:
    app.config['MONGOALCHEMY_DATABASE'] = 'watchit'

db = MongoAlchemy(app)

from User import User

oauth = OAuth()
twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key=TWITTER_APP_ID,
    consumer_secret=TWITTER_APP_SECRET,
    request_token_params={'scope': 'email'}
)
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

app.secret_key = SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)



@app.route('/')
def home_page():
#    try:
#        print mongo.db.openshift.find_one()
#    except Exception, e:
#        print e
#    o = twitter.get('statuses/show/')
    if  current_user.is_authenticated():
        return render_template('home.html',current_user=current_user)
    else:
        return render_template('login.html',current_user=current_user)

@app.route('/login/twitter')
def login_twitter():
    return twitter.authorize(callback=url_for('twitter_authorized',
        next=request.args.get('next') or request.referrer or None))

@app.route('/login/facebook')
def login_facebook():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@login_manager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/login/twitter/authorized')
@twitter.authorized_handler
def twitter_authorized(resp):
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
    user = User(id=resp['screen_name'], name=resp['screen_name'])
    user.save()

    # http://packages.python.org/Flask-Login/
    login_user(user)
    return redirect(next_url)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/login/facebook/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('home_page')
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
            )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    flash('Logged in as id=%s name=%s redirect=%s' %\
           (me.data['id'], me.data['name'], request.args.get('next')))
    user = User.query.filter(User.id == me.data['id']).first()
    if not user:
        user = User(id=me.data['id'])
    user.name = me.data['name']
    user.email = me.data['email']
    user.save()
    login_user(user)
    return redirect(next_url)


@app.errorhandler(OAuthException)
def handle_oauth_exception(error):
    return 'OAuthException, please try later.'

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))


if __name__ == '__main__':

    app.run(debug=True)