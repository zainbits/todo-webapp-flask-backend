import datetime
import uuid

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from project import db
from project.decorators import make_secure
from project.todo.models import Todo
from project.todo.schema import TodoSchema
from project.user.models import User
from project.user.schema import UserSchema
from sqlalchemy.exc import InvalidRequestError
from werkzeug.security import check_password_hash, generate_password_hash

todo = Blueprint('todo', __name__)

users_schema = UserSchema(many=True)
user_schema = UserSchema()

todos_schema = TodoSchema(many=True)
todo_schema = TodoSchema()


@todo.route('/todo', methods=['POST'])
@jwt_required()
def create_todo():
    data = request.get_json()
    current_user = get_jwt_identity()
    current_user = User.query.filter_by(name=current_user).first()
    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'msg': 'TODO Created'}), 200


@todo.route('/admin/todo/allusers', methods=['GET'])
@jwt_required()
@make_secure('admin')
def get_allusers_todos():
    todos = Todo.query.all()
    todos = todos_schema.dump(todos)
    return jsonify(todos)


@todo.route('/todo', methods=["GET"])
@jwt_required()
def get_all_todos():
    try:
        current_user = get_jwt_identity()
    except Exception as e:
        print(e)
    current_user = User.query.filter_by(name=current_user).first()
    todos = Todo.query.filter_by(user_id=current_user.id)
    todos = todos_schema.dump(todos)
    return jsonify(todos), 200


@todo.route('/todo/<todo_id>', methods=['PUT'])
@jwt_required()
def update_a_todo(todo_id):
    try:
        current_user = get_jwt_identity()
        current_user = User.query.filter_by(name=current_user).first()
        todo = Todo.query.filter_by(
            user_id=current_user.id, id=todo_id).first()

        if not todo:
            return jsonify({'message': 'todo not found'}),\
                404

        data = request.get_json()
        todo = Todo.query.filter_by(
            user_id=current_user.id, id=todo_id).\
            update(data)

        db.session.commit()

        todo = Todo.query.filter_by(
            user_id=current_user.id, id=todo_id).first()
        todo = todo_schema.dump(todo)

        return jsonify({
            'message': 'updated successfully',
            'todo': todo
        }),\
            204
    except (InvalidRequestError):
        return jsonify({
            'message': 'wrong keys passed'
        }),\
            400


@todo.route('/todo/<todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user = get_jwt_identity()
    user = User.query.filter_by(name=user).first()
    todo = Todo.query.\
        filter_by(id=todo_id, user_id=user.id).first()

    if not todo:
        return jsonify({'message': 'todo not found'}),\
            404

    db.session.delete(todo)
    db.session.commit()
    todo = todo_schema.dump(todo)
    return jsonify({'message': 'deleted successfully',
                    'todo': todo}), 200


@todo.route("/admin/todo/<todo_id>", methods=["DELETE"])
@jwt_required()
@make_secure("admin")
def delete_any_todo(todo_id):
    todo = Todo.query.\
        filter_by(id=todo_id).first()

    if not todo:
        return jsonify({'message': 'todo not found'}),\
            404

    db.session.delete(todo)
    db.session.commit()
    todo = todo_schema.dump(todo)
    return jsonify({'message': 'deleted successfully',
                    'todo': todo}), 200
