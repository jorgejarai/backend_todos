import hashlib
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
jwt = JWTManager(app)

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri, server_api=ServerApi(version='1'))

db = client['udec']
users = db['users']

@app.route('/api/v1/users', methods=['POST'])
@jwt_required()
def create_user():  
    new_user = request.get_json()
    new_user['password'] = hashlib.sha256(new_user['password'].encode('utf-8')).hexdigest()
    doc = users.find_one({
        "username": new_user['username']
    })

    if doc:
        return jsonify({
            "success": False,
            "message": "Username already exists"
        }), 400
    
    users.insert_one(new_user)
    return jsonify({
        "success": True,
        "message": "User created successfully"
    }), 201

@app.route('/api/v1/login', methods=['POST'])
def login():  
    login_details = request.get_json()
    user = users.find_one({"username": login_details['username']})
    
    if user:
        enc_pass = hashlib.sha256(login_details['password'].encode('utf-8')).hexdigest()
        if enc_pass == user['password']:
            access_token = create_access_token(identity=str(user['username']))
            return jsonify(access_token=access_token), 200
        
    return jsonify({"success": False, "message": "Wrong credentials"}), 401


if __name__ == '__main__':
    app.run(debug=True, port=5000)
