from __main__ import app

from flask import request, jsonify
from flask_jwt_extended import jwt_required

from database import Database

todos = Database().pymongo.db.todos


@app.route('/api/v1/todos', methods=['GET'])
@jwt_required()
def get_todos():
    return jsonify({
        "success": True,
    }), 200


@app.route('/api/v1/todos', methods=['POST'])
@jwt_required()
def create_todo():
    return jsonify({
        "success": True,
    }), 201


@app.route('/api/v1/todos/<id>', methods=['GET'])
@jwt_required()
def get_todo():
    return jsonify({
        "success": True,
    }), 200


@app.route('/api/v1/todos/<id>', methods=['PUT'])
@jwt_required()
def update_todo():
    return jsonify({
        "success": True,
    }), 200


@app.route('/api/v1/todos/<id>', methods=['DELETE'])
@jwt_required()
def delete_todo():
    return jsonify({
        "success": True,
    }), 200
