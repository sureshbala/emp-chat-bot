from api import app, mongo, apiV1
from flask import jsonify,request,render_template, send_from_directory
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,requestJsonData,getPersonName,getPlaceName,sendOTP
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
import pandas as pd
import datetime
from random import randrange

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_raw_jwt,fresh_jwt_required,jwt_optional
)


@app.route('/assets/<path:path>', methods=['GET'])
def render_assets(path):
    try:
        return send_from_directory('static/assets/', path)
    except:
        return {'error': "Internal Server Error : "+str(e)},500
    

  
@app.route('/a/<id>', methods=['GET'])
def render_static1(id):
    try:
        result = mongo.db.LAS.find_one({"_id":getId(id)})
        if not result:
           return {'error': "Internal Server Error"},500
        mobile = ''
        if result['active'] == 1:
            mobile = str(result['mobile'])
           
        #return send_from_directory('static', "index.html")
        return render_template("index.html",base_url='/a/'+id+'/',mobile=mobile)
    except:
        return {'error': "Internal Server Error"},500
    
    
@app.route('/a/<id>/<page>', methods=['GET'])
def render_static2(id,page):
    try:
        result = mongo.db.LAS.find_one({"_id":getId(id)})
        if not result:
           return {'error': "Internal Server Error"},500
        mobile = ''
        if result['active'] == 1:
            mobile = str(result['mobile'])
           
        #return send_from_directory('static', "index.html")
        return render_template("index.html",base_url='/a/'+id+'/',mobile=mobile)
    except:
        return {'error': "Internal Server Error"},500





@apiV1.resource('/register/return')
class RegisterReturn(Resource):
    
    def __init__(self):
        self.create_fields = {'mobile': {'type': 'number','required': True,'empty': False}}
        
    
    def post(self):
        try:
           
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
                mobile = request.json.get('mobile', None)
                
                result = mongo.db.LAS.find_one({"mobile":int(mobile)})
                if not result :
                    return {"error": "Mobile number is not a valid."}, 400
                
                #sendOTP(int(mobile))
                #result = mongo.db.LAS.update({"_id":result['_id']},{'$set':{'fwp':str(get_jwt_identity())}})
               
                identity = str(mobile)
                expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
                refresh_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
                ret = {
                    'token': {'access': create_access_token(identity=identity,expires_delta=expires,user_claims={'step':'register'}),
                              'refresh': create_refresh_token(identity=identity,expires_delta=refresh_expires,user_claims={'step':'register'})},
                    'profile': {},
                }
                return ret, 200
            else:
                return {'error':v.errors},400
        except Exception as e:
            return {'error': "Internal Server Error : "+str(e)},500
    
  

@apiV1.resource('/register')
class Register(Resource):
    
    def __init__(self):
        self.create_fields = {'mobile': {'type': 'number','required': True,'empty': False}}
        
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            #return json,200
            if v.validate(json):
                mobile = request.json.get('mobile', None)
                
                result = mongo.db.LAS.find_one({"mobile":int(mobile)})
                if not result :
                    return {"error": "Mobile number is not a valid."}, 400
                
                sendOTP(int(mobile))
                result = mongo.db.LAS.update({"_id":result['_id']},{'$set':{'fwp':str(get_jwt_identity())}})
               
                identity = str(mobile)
                expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
                refresh_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
                ret = {
                    'token': {'access': create_access_token(identity=identity,expires_delta=expires,user_claims={'step':'otp'}),
                              'refresh': create_refresh_token(identity=identity,expires_delta=refresh_expires,user_claims={'step':'otp'})},
                    'profile': {},
                }
                return ret, 200
            else:
                return {'error':v.errors},400
        except Exception as e:
            return {'error': "Internal Server Error : "+str(e)},500
    
    def get(self):
        try:
            identity = get_jwt_identity()       
            #print(identity)
            result = mongo.db.LAS.find_one({"mobile":int(identity)})
            if not result :
                return {"error": "Something wrong."}, 400
            sendOTP(int(identity))
            
            return {'status':'ok'},200
        
        except Exception as e:
            return {'error': "Internal Server Error : "+str(e)},400

@apiV1.resource('/register/otp')
class RegisterOtp(Resource):
    
    def __init__(self):
        self.create_fields = {'code': {'type': 'number','required': True,'empty': False}}
        
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            #return json,200
            if v.validate(json):
                identity = get_jwt_identity()
                #print(identity)
                code = request.json.get('code', None)
                
                #print(code)
                result = mongo.db.LAS.find_one({"mobile":int(identity)})
                step = "terms"
                if not result :
                    return {"eroor": "OTP is not a valid."}, 400
                
                
                    
                    
                    
                minutes_diff = (datetime.datetime.now() - result['otp_at']).total_seconds() / 60.0
                #print(datetime.datetime.now())
                #print(minutes_diff)
                if str(result['otp']) != str(code) or minutes_diff > 15:
                    return {"error": "OTP is not a valid or expired."}, 400
                
                if result['active'] == 1:
                    step = "welcome"
                else:
                    result = mongo.db.LAS.update({"_id":result['_id']},{'$set':{'active':1,'active_at':datetime.datetime.now()}})
                
                
                expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
                refresh_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
                
                ret = {
                    'token': {'access': create_access_token(identity=identity,expires_delta=expires,user_claims={'step':step}),
                              'refresh': create_refresh_token(identity=identity,expires_delta=refresh_expires,user_claims={'step':step})},
                    'profile': {},
                    'step':step
                }
                return ret, 201
            else:
                return {'error':v.errors},400
        except Exception as e:
            return {'error': "Internal Server Error : "+str(e)},500
        
    
        
        

@apiV1.resource('/register/terms')
class RegisterTerms(Resource):
    
    def __init__(self):
        self.create_fields = {'code': {'type': 'number','required': True,'empty': False}}
        
    
    def post(self):
        try:
            identity = get_jwt_identity()
            expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
            refresh_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
            ret = {
                'token': {'access': create_access_token(identity=identity,expires_delta=expires,user_claims={'step':'welcome'}),
                          'refresh': create_refresh_token(identity=identity,expires_delta=refresh_expires,user_claims={'step':'welcome'})},
                'profile': {},
            }
            return ret, 200
           
        except Exception as e:
            return {'error': "Internal Server Error : "+str(e)},500


        
@apiV1.resource('/register/thankyou')
class RegisterThankyou(Resource):
    
    def __init__(self):
        self.create_fields = {'code': {'type': 'number','required': True,'empty': False}}
        
    
    def post(self):
        try:
            identity = get_jwt_identity()
            expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
            refresh_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
            ret = {
                'token': {'access': create_access_token(identity=identity,expires_delta=expires,user_claims={'step':'thankyou'}),
                          'refresh': create_refresh_token(identity=identity,expires_delta=refresh_expires,user_claims={'step':'thankyou'})},
                'profile': {},
            }
            return ret, 200
           
        except Exception as e:
            return {'error': "Internal Server Error : "+str(e)},500        
                
 
 
"""        
#@apiV1.resource('/import/fwp/<text>')
class ImportFWP(Resource):
    
    def __init__(self):
        self.create_fields = {'otp': {'type': 'number','required': True,'empty': False}}
        
    
    def get(self,text):
        #place = getPlaceName(text)
        
        name = getPersonName(text)
        return name
    
    def get1(self):
        try:
            c = 1
            df = pd.read_csv('questions.csv', sep=",")
            for index, row in df.iterrows():
                #print(row)
                #print(row['Question Type'],row['Questions'],row['Options'])
                #print(row['Options'] ":")
                t = {}
                t['label'] = row['Questions']
                t['type'] = row['Question Type']
                
                if str(row['Options']) != "nan":
                    t['options'] = str(row['Options']).split("\n")
                else:
                    t['options'] = []
                    
                if str(row['Templates']) != "nan":
                    t['templates'] = str(row['Templates']).split("\n")
                else:
                    t['templates'] = []
                
                t['validation'] = {"type" : "string","required" : False,"empty": False}
                t['priority'] = c
                t['status'] = 1
                c = c+1
                #if t['type'] == "OPEN" or t['type'] == 'MCQ':
                #mongo.db.questions1.insert(t)
            
            print(df)
        except Exception as e:
            return {'error': "Internal Server Error" + str(e)},500
        
        
    def get1(self):
        try:
            df = pd.read_csv('FWP.csv', sep=",")
            for index, row in df.iterrows():
                print(row)
                #mongo.db.fwp_codes.insert({'name':row['FWP'],'code':row['Code'],'status':1})
            
            #print(df)
        except Exception as e:
            return {'error': "Internal Server Error" + str(e)},500"""
 
 
 
 
 
 
 
 
 
 
 
 
 
 
           