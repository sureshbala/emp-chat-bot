from api import app
from api import Api
from api.models import Printer
from flask import render_template
from flask import Flask, jsonify, request
#
from api.controller import auth,login,ivr
