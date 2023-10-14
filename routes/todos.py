from __main__ import app
from bson import ObjectId

from bson import json_util, ObjectId
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from functools import wraps

from database import Database

todos = Database().pymongo.db.todos
users = Database().pymongo.db.users

reqAuth = False

# Custom decorator to conditionally apply @jwt_required


def custom_jwt_required(view_func):
    @wraps(view_func)
    def decorated_view(*args, **kwargs):
        if reqAuth:
            return jwt_required()(view_func)(*args, **kwargs)
        else:
            return view_func(*args, **kwargs)

    return decorated_view


@app.route('/api/v1/todos', methods=['GET'])
@custom_jwt_required
def get_todos():
    currentUser = request.get_json().get("currentUser")

    matching_todos = todos.find({"createdBy": currentUser})
    # matching_todos = todos.find({"createdBy": currentUser}, {"_id": 0})
    # matching_todos = list(matching_todos)
    # matching_todos = [json_util.dumps(todo) for todo in matching_todos]
    matching_todos = [json_util.dumps(todo, default=str)
                      for todo in matching_todos]
    # formatted_todos = []
    # for todo in matching_todos:
    #     formatted_todo = {
    #         # "_id": str(todo["_id"]),
    #         "createdBy": todo["createdBy"],
    #         "title": todo["title"],
    #         "description": todo["description"],
    #         "startDate": todo["startDate"],
    #         "endDate": todo["endDate"],
    #         "labels": todo["labels"]
    #     }
    #     formatted_todos.append(formatted_todo)

    # #  deberíamos verificar cuando no hay TODOS?

    return jsonify({
        "success": True,
        "todos": matching_todos
    }), 200


@app.route('/api/v1/todos', methods=['POST'])
@custom_jwt_required
def create_todo():
    new_todo = request.get_json()

    if not all(key in new_todo for key in ("createdBy", "title", "description", "startDate", "endDate", "labels")):
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400

    if not isinstance(new_todo["labels"], list):
        return jsonify({
            "success": False,
            "message": "Labels should be a list"
        }), 400

    todos.insert_one(new_todo)

    return jsonify({
        "success": True,
        "message": "TODO created successfully"
    }), 201


@app.route('/api/v1/todos/<id>', methods=['GET'])
@custom_jwt_required
def get_todo(id):
    # need to catch an error where <id> is not a valid OjbetcId
    # bson.errors.InvalidId: '652ac5ac62a3529a24f8a98p' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string
    result = todos.find_one({"_id": ObjectId(id)})

    if result is not None:
        return jsonify({
            "success": True,
            "todo": {
                "createdBy": result["createdBy"],
                "title": result["title"],
                "description": result["description"],
                "startDate": result["startDate"],
                "endDate": result["endDate"],
                "labels": result["labels"]
            }
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "couldn't find TODO"
        }), 404


@app.route('/api/v1/todos/<id>', methods=['PUT'])
@custom_jwt_required
def update_todo(id):
    existing_todo = todos.find_one({"_id": ObjectId(id)})

    if existing_todo is None:
        return jsonify({"success": False, "message": "TODO not found"}), 404

    # Get the updated data from the request JSON
    updated_data = request.get_json()

    # Update the todo with the new data
    result = todos.update_one({"_id": ObjectId(id)}, {
                              "$set": updated_data})

    if result.modified_count == 1:
        return jsonify({"success": True, "message": "Todo updated successfully"}), 200
    else:
        return jsonify({"success": False, "message": "Failed to update todo"}), 500


@app.route('/api/v1/todos/<id>', methods=['DELETE'])
@custom_jwt_required
def delete_todo(id):
    existing_todo = todos.find_one({"_id": ObjectId(id)})

    if existing_todo is None:
        return jsonify({"success": False, "message": "TODO not found"}), 404

    result = todos.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 1:
        return jsonify({
            "success": True,
            "message": "TODO deleted successfully"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Failed to delete TODO",
            "id": id
        }), 500
