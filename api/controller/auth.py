from api import app, mongo
from flask import Flask, jsonify, request
import json
import hashlib 
from api.lib.helper import getData,getId
from bson.int64 import Int64
#from datetime import datetime, date
import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_raw_jwt,fresh_jwt_required,jwt_optional
)


jwt = JWTManager(app)
blacklist = set()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

"""@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    result = mongo.db.fwp_codes.find_one({"_id":getId(identity)})
    return getData(result)"""

@app.route('/login', methods=['POST'])
def login():
    
    try:
        code = request.json.get('code', None)
    
        code = code.replace('"', '')
        result = mongo.db.fwp_codes.find_one({"code":code})
        fwp = []
        
        if not result :
            return jsonify({"msg": "Activation code is not a valid."}), 401
        
        
        fwp = getData(result)
        identity = fwp['code']
        del fwp['code']
        
        expires = app.config['JWT_ACCESS_TOKEN_EXPIRES']
        refresh_expires = app.config['JWT_REFRESH_TOKEN_EXPIRES']
        ret = {
            'token': {'access': create_access_token(identity=identity,expires_delta=expires,user_claims={'step':'register'}),
                      'refresh': create_refresh_token(identity=identity,expires_delta=refresh_expires,user_claims={'step':'register'})},
            'profile': fwp,
        }
        
        return jsonify(ret), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 401





@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(minutes=10800)
    new_token = create_access_token(identity=current_user,expires_delta=expires, user_claims={'step':'step1'})
    ret = {'token':{'access': new_token}}
    return jsonify(ret), 200


@app.route('/logout', methods=['DELETE'])
@jwt_optional
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

@app.route('/protected', methods=['GET'])
def protected():
    app.logger.info('Processing default request')
    username = get_jwt_identity()
    tt = get_raw_jwt()
    return jsonify(logged_in_as=tt), 200



