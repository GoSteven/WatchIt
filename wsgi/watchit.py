from flask import Flask
from flask.ext.pymongo import PyMongo
import json
from bson import json_util
import os

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ['OPENSHIFT_MONGODB_DB_URL'] + os.environ['OPENSHIFT_APP_NAME'] + '?auto_start_request=true'
mongo = PyMongo(app)

@app.route('/')
def home_page():
    return str(json.dumps(mongo.db.openshift.find_one()))







if __name__ == '__main__':
    app.run()