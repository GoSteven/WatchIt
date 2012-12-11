from flask import Flask
from flask.ext.pymongo import PyMongo
import json
from bson import json_util
import os

app = Flask(__name__)
#app.config['MONGO_URI'] = os.environ['OPENSHIFT_MONGODB_DB_URL'] + os.environ['OPENSHIFT_APP_NAME'] + '?auto_start_request=true'
app.config['MONGO_HOST'] = os.environ['OPENSHIFT_MONGODB_DB_HOST']
app.config['MONGO_USERNAME'] = os.environ['OPENSHIFT_MONGODB_DB_USERNAME']
app.config['MONGO_PASSWORD'] = os.environ['OPENSHIFT_MONGODB_DB_PASSWORD']
app.config['MONGO_DBNAME'] = os.environ['OPENSHIFT_APP_NAME']

mongo = PyMongo(app)

@app.route('/')
def home_page():
#    return 'hello steven'
    try:
        print mongo.db.openshift.find_one()
    except Exception, e:
        print e
    return 'hello steven'







if __name__ == '__main__':
    app.run()