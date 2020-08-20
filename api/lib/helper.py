from api import app, mongo
from bson import ObjectId
from pymongo.cursor import Cursor
import json
import unicodedata
from flask import request
from datetime import date,datetime
from flask_jwt_extended import get_jwt_identity,get_jwt_claims
import re
import pandas as pd
import spacy
from spacy import displacy
import en_core_web_lg
nlp = spacy.load('en_core_web_lg')

import urllib.request
from urllib.parse import urlencode
import requests
from random import randrange
          
def getCurrentUser():
    return get_jwt_claims()

def getCurrentUserId():
    return get_jwt_identity()


def dateTimeValidate(date):
        try:
            return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except:
            return False
        

def getActivity(data):
    temp = []
    try:
        for row in data:
            t = {}
            t['start'] = getRow(row['start'])
            t['end'] = getRow(row['end'])
            if 'selfie' in row:
                t['selfie'] = row['selfie']
            temp.append(t)
            
    except Exception as e:
        print(e)
        
    return temp
        
def getRow(row):
    try:
        for k in row.keys(): 
            
            if isinstance(row[k], ObjectId):
                row[k] = str(row[k])
            elif isinstance(row[k], datetime):
                row[k] = str(row[k])
            
            if k == '_id':
                row['id'] = str(row[k])
                row.pop('_id') 
            elif k == "profile_pic":
                row['profile_pic'] =  app.config['BASE_URL']+row['profile_pic']
                
        return row
    except:
        return None

    
def getData(data):
    temp = []
    if isinstance(data, Cursor):
        for row in data:
            temp.append(getRow(row))
        return temp
    else:
        return getRow(data)


def getId(id):
    try:
        return ObjectId(id)
    except:
        return False

def _decode(o):
    # Note the "unicode" part is only for python2
    if isinstance(o, str) or isinstance(o, unicodedata):
        try:
            return int(o)
        except ValueError:
            return o
    elif isinstance(o, dict):
        return {k: _decode(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_decode(v) for v in o]
    else:
        return o

def requestJsonData():  
    json_data = request.get_json()  
    print(json_data)
    json_data = json.dumps(json_data);
    print(json_data)
    return json.JSONDecoder(json_data)
    
    
    
def _parseJSON(obj):
    newobj = {}

    for key, value in obj.iteritems():
        key = str(key)

        if isinstance(value, dict):
            newobj[key] = _parseJSON(value)
        elif isinstance(value, list):
            if key not in newobj:
                newobj[key] = []
                for i in value:
                    newobj[key].append(_parseJSON(i))
        elif isinstance(value, str):
            val = str(value)
            if val.isdigit():
                val = int(val)
            else:
                try:
                    val = float(val)
                except ValueError:
                    val = str(val)
            newobj[key] = val

    return newobj 
 
class CustomJSONDecoder(json.JSONDecoder):
    def default(self, o):
        return json.loads(o, object_hook=lambda d: {int(v) if v.lstrip('-').isdigit() else v: v for k, v in d.items()})
 
 
 

def getPlaceName(text):
    text = text.lower().split(' ')
    print(text)
    #print("Input : " + text)
    
    #print(result)
    return "Unknown Person" 
 
def getPersonName(text):
    #print("Input : " + text)
    result,length  = nameExtractor("person",text.lower())
    if length > 0:
        return result[0]

    #print(result)
    return "Unknown Person"

def nameExtractor(choice,rawtext):
    try:
        #print(re.search('\s', rawtext))
        if ' ' not in rawtext:
            return [rawtext],1
            
            
        doc = nlp(rawtext)
        d = []
        ORG_named_entity = []
        PERSON_named_entity = []
        GPE_named_entity = []
        MONEY_named_entity = []
        
        for ent in doc.ents:
            #print(ent)
            d.append((ent.label_, ent.text))
            
            df = pd.DataFrame(d, columns=('named entity', 'output'))
            #print(df)
            ORG_named_entity = df.loc[df['named entity'] == 'ORG']['output']
            PERSON_named_entity = df.loc[df['named entity'] == 'PERSON']['output']
            GPE_named_entity = df.loc[df['named entity'] == 'GPE']['output']
            MONEY_named_entity = df.loc[df['named entity'] == 'MONEY']['output']
            
        if choice == 'organization':
            results = ORG_named_entity
            num_of_results = len(results)
        elif choice == 'person':
            results = PERSON_named_entity
            num_of_results = len(results)
        elif choice == 'geopolitical':
            results = GPE_named_entity
            num_of_results = len(results)
        elif choice == 'money':
            results = MONEY_named_entity
            num_of_results = len(results)
        #print(results)    
        return list(results),num_of_results
    except Exception as e:
        print(e)
        return [],0
        
        


def sendOTP(mobile):
        try:
            id = ObjectId()
            result = mongo.db.LAS.find_one({'mobile':int(mobile)})

            if result:
                id = result['_id']
            
            otp = randrange(1000, 9999, 4)
            msg = "Hi! Here's your OTP - "+str(otp)
            msg = urllib.parse.quote(msg)
            url = "http://truebulksms.biz/api.php?username=Surbotxn&password=342880&sender=KINBOT&sendto=91"+str(mobile)+"&message="+msg
            
            #return mongo.db.LAS.update({"_id":result['_id']},{'$set':{'otp':otp,'otp_at':datetime.now()}})
            
            r = requests.get(url)
            #print(r.status_code)
            if(r.status_code == 200):
                result = mongo.db.LAS.update({"_id":result['_id']},{'$set':{'otp':otp,'otp_at':datetime.now()}})
                
            return id
           
        except Exception as e:
            print(e)
            return False 
 