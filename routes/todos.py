from __main__ import app
from bson import ObjectId

from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from database import Database

todos = Database().pymongo.db.todos
users = Database().pymongo.db.users


@app.route('/api/v1/todos', methods=['GET'])
@jwt_required()
def get_todos():
    user = users.find_one({"username": get_jwt_identity()})

    user_todos = list(todos.find({"created_by": user['_id']}))

    for todo in user_todos:
        todo["_id"] = str(todo["_id"])
        todo["created_by"] = str(todo["created_by"])

    return jsonify({
        "success": True,
        "todos": user_todos
    }), 200


@app.route('/api/v1/todos', methods=['POST'])
@jwt_required()
def create_todo():
    new_todo = request.get_json()

    user = users.find_one({"username": get_jwt_identity()})

    new_todo['created_by'] = user['_id']
    saved_todo = todos.insert_one(new_todo)

    return jsonify({
        "success": True,
        "todoId": str(saved_todo.inserted_id),
    }), 201


@app.route('/api/v1/todos/<todo_id>', methods=['GET'])
@jwt_required()
def get_todo(todo_id):
    todo = todos.find_one({"_id": ObjectId(todo_id)})

    if not todo:
        return jsonify({
            "success": False,
            "message": "Todo not found"
        }), 404

    user = users.find_one({"username": get_jwt_identity()})

    if todo['created_by'] != user['_id']:
        return jsonify({
            "success": False,
            "message": "Todo not founnd"
        }), 404

    todo["_id"] = str(todo["_id"])
    todo["created_by"] = str(todo["created_by"])

    return jsonify({
        "success": True,
        "todo": todo
    }), 200


@app.route('/api/v1/todos/<todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    todo = todos.find_one({"_id": ObjectId(todo_id)})

    if not todo:
        return jsonify({
            "success": False,
            "message": "Todo not found"
        }), 404

    user = users.find_one({"username": get_jwt_identity()})

    if todo['created_by'] != user['_id']:
        return jsonify({
            "success": False,
            "message": "Todo not founnd"
        }), 404

    request.get_json().pop("_id", None)
    request.get_json().pop("created_by", None)

    todos.update_one({"_id": ObjectId(todo_id)}, {"$set": request.get_json()})

    return jsonify({
        "success": True,
    }), 200


@app.route('/api/v1/todos/<todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    todo = todos.find_one({"_id": ObjectId(todo_id)})

    if not todo:
        return jsonify({
            "success": False,
            "message": "Todo not found"
        }), 404

    user = users.find_one({"username": get_jwt_identity()})

    if todo['created_by'] != user['_id']:
        return jsonify({
            "success": False,
            "message": "Todo not founnd"
        }), 404

    todos.delete_one({"_id": ObjectId(todo_id)})

    return jsonify({
        "success": True,
    }), 200
