# -*- coding: utf-8 -*-

__version__ = '0.1'

from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from api.lib.mongoflask import *
from flask_cors import CORS,cross_origin
import datetime
import logging
from flask_json import FlaskJSON, JsonError, json_response, as_json
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO
import os


app = Flask('api')

CORS(app, support_credentials=True,resources={r"*": {"origins": "*"}})

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='app.log', level=logging.DEBUG)

app.config['SECRET_KEY'] ='tq$Nv"rE`+93K<tY{aSx8"&:.]4{Gf56U'


app.config["MONGO_URI"] = "mongodb://pmi:Title321@localhost:27017/pmi_chatbot"


app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['JWT_SECRET_KEY'] = 'tq$Nv"rE`+93K<tY{aSx8"&:.]4{Gf56U'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=10800)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=10800)
app.config['JWT_BLACKLIST_ENABLED'] = True

app.config['BASE_URL'] = "https://chat-bot.in/"


UPLOAD_FOLDER = 'uploads/'

app.config['UPLOAD_FOLDER'] = os.path.join(UPLOAD_FOLDER)

apiV1 = Api(app)
mongo = PyMongo(app)

socketio = SocketIO(app,async_mode="threading",cors_allowed_origins="*",ping_interval=2000,ping_timeout=120000)

#socketio = SocketIO(async_mode="threading")
#socketio.init_app(app)

#socketio.init_app(app,cors_allowed_origins="*",ping_interval=2000,ping_timeout=120000)
#socketio.run(app,host="0.0.0.0",port=8988)


import api.models
import api.controller
import api.controller.chatEvents



