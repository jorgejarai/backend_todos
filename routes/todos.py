from __main__ import app
from bson import ObjectId

from bson import json_util, ObjectId
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from functools import wraps

from database import Database

todos = Database().pymongo.db.todos
users = Database().pymongo.db.users

reqAuth = True


def custom_jwt_required(view_func):
    """Custom decorator to conditionally apply @jwt_required"""
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
    currentUser = users.find_one({"username": get_jwt_identity()})

    matching_todos = todos.find({"createdBy": ObjectId(currentUser["_id"])})
    matching_todos = [{**todo, "_id": str(todo["_id"]), "createdBy": str(todo['createdBy'])}
                      for todo in matching_todos]

    return jsonify({
        "success": True,
        "todos": matching_todos
    }), 200


@app.route('/api/v1/todos', methods=['POST'])
@custom_jwt_required
def create_todo():
    new_todo = request.get_json()

    if not all(key in new_todo for key in ("title", "description", "startDate", "endDate", "labels")):
        return jsonify({
            "success": False,
            "message": "Missing required fields"
        }), 400

    if not isinstance(new_todo["labels"], list):
        return jsonify({
            "success": False,
            "message": "Labels should be a list"
        }), 400

    currentUser = users.find_one({"username": get_jwt_identity()})
    new_todo["createdBy"] = ObjectId(currentUser["_id"])

    new_todo.pop("_id", None)

    todos.insert_one(new_todo)

    return jsonify({
        "success": True,
        "message": "TODO created successfully"
    }), 201


@app.route('/api/v1/todos/<id>', methods=['GET'])
@custom_jwt_required
def get_todo(id):
    result = todos.find_one({"_id": ObjectId(id)})

    if result is not None:
        currentUser = users.find_one({"username": get_jwt_identity()})
        if result["createdBy"] != ObjectId(currentUser["_id"]):
            return jsonify({
                "success": False,
                "message": "TODO not found"
            }), 404

        return jsonify({
            "success": True,
            "todo": {
                **result,
                "_id": str(result["_id"]),
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

    currentUser = users.find_one({"username": get_jwt_identity()})
    if existing_todo["createdBy"] != ObjectId(currentUser["_id"]):
        return jsonify({
            "success": False,
            "message": "TODO not found"
        }), 404

    # Get the updated data from the request JSON
    updated_data = request.get_json()

    # Remove _id and createdBy from the updated data
    updated_data.pop("_id", None)
    updated_data.pop("createdBy", None)

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

    currentUser = users.find_one({"username": get_jwt_identity()})
    if existing_todo["createdBy"] != ObjectId(currentUser["_id"]):
        return jsonify({
            "success": False,
            "message": "TODO not found"
        }), 404

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


@app.route('/api/v1/todos', methods=['DELETE'])
@custom_jwt_required
def delete_all_todos():
    currentUser = users.find_one({"username": get_jwt_identity()})

    result = todos.delete_many({"createdBy": ObjectId(currentUser["_id"])})

    if result.deleted_count > 0:
        return jsonify({
            "success": True,
            "message": "TODOs deleted successfully"
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": "Failed to delete TODOs"
        }), 500
