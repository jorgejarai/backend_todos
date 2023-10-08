from __main__ import app

from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token
import hashlib

from database import Database

users = Database().pymongo.db.users

@app.route('/api/v1/users', methods=['POST'])
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
            return jsonify({
                "success": True,
                "access_token": access_token
            }), 200
        
    return jsonify({"success": False, "message": "Wrong credentials"}), 401

@app.route('/api/v1/users/me', methods=['GET'])
@jwt_required()
def get_me():
    return jsonify({
        "success": True,
    }), 200
