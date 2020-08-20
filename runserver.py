#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api import app, mongo, socketio
#import api
from api.models import printer
from http import HTTPStatus
from flask import Flask, jsonify, request,abort
from flask_jwt_extended import verify_jwt_in_request,jwt_required
from datetime import datetime

@app.errorhandler(404)
def not_found404(e):
    return jsonify({"error":"The Requested API instance was not found."}),404
 
 
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error":"Internal Server Error."}),500
  
@app.errorhandler(502)
def internal_error(e):
    return jsonify({"error":"Internal Server Error."}),200

@app.before_request
def before_request():
    if not (request.endpoint == 'login' or request.endpoint == 'refresh' or request.endpoint == 'render_static1' or request.endpoint == 'render_static2' 
            or request.endpoint == "render_assets" or request.endpoint == "render_assets1" or request.endpoint == "registerreturn" 
            or request.endpoint == "importfwp" or request.endpoint == "ivr"):
        #jwt_required()
        verify_jwt_in_request()
        #return jsonify({"msg": request.endpoint}),200

       
@app.after_request
def after_request(response):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    print(request.endpoint)
    json = {}
    json['uri'] = request.endpoint
    json['ip'] = ip
    json['request'] = request.get_json(force=True, silent=True)
    json['response'] = response.get_json()
    json['created_at'] = datetime.now()
    mongo.db.logs.insert_one(json)
    
    return response

if __name__=='__main__':
    #app.run('0.0.0.0',debug=True)
    socketio.run(app,host="0.0.0.0",port="5000",debug=False)
