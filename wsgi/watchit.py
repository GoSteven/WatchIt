from flask import Flask
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps
import os

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ['OPENSHIFT_MONGODB_DB_URL'] + os.environ['OPENSHIFT_APP_NAME']
mongo = PyMongo(app)

@app.route('/')
def home_page():
    return dumps(mongo.db.openshift.find_one())







if __name__ == '__main__':
    app.run()