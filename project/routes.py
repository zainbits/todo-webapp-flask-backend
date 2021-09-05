import uuid
import datetime

from project import app, db
from project.decorators import make_secure
from project.user.models import User
from project.user.schema import UserSchema
from project.todo.models import Todo
from project.todo.schema import TodoSchema

from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.exc import InvalidRequestError

users_schema = UserSchema(many=True)
user_schema = UserSchema()

todos_schema = TodoSchema(many=True)
todo_schema = TodoSchema()


@app.route('/user', methods=['GET'])
def get_all_users():
    users = User.query.all()
    data = users_schema.dump(users)
    return jsonify(data)


@app.route('/user/<public_id>', methods=['GET'])
@jwt_required()
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'no user found!'})

    data = user_schema.dump(user)
    return jsonify(data)


@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "New user created"})


@app.route('/user/<public_id>', methods=['PUT'])
@jwt_required()
@make_secure('admin')
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "no user found"})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "user has been promoted to admin"})


@app.route('/user/<public_id>', methods=['DELETE'])
@jwt_required()
@make_secure('admin')
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "no user found"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "the user has been deleted"})


@app.route('/login')
def login():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response({'message': 'Could not verify'},  401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response({'message': 'Could not verify'},  401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    if check_password_hash(user.password, auth.password):
        token = create_access_token(
            identity=user.name, expires_delta=datetime.timedelta(minutes=30))
        return jsonify({'token': token})

    return make_response({'message': 'Could not verify'},  401, {'WWW-Authenticate': 'Basic realm="Login required"'})


@app.route('/about', methods=['GET'])
@jwt_required()
def about():
    current_user = get_jwt_identity()
    current_user = User.query.filter_by(name=current_user).first()
    user = user_schema.dump(current_user)
    return jsonify({'user': user}), 200


@app.route('/todo', methods=['POST'])
@jwt_required()
def create_todo():
    data = request.get_json()
    current_user = get_jwt_identity()
    print(current_user)
    current_user = User.query.filter_by(name=current_user).first()
    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'msg': 'TODO Created'})


@app.route('/todo/allusers', methods=['GET'])
@jwt_required()
@make_secure('admin')
def get_allusers_todos():
    todos = Todo.query.all()
    todos = todos_schema.dump(todos)
    return jsonify(todos)


@app.route('/todo', methods=["GET"])
@jwt_required()
def get_all_todos():
    current_user = get_jwt_identity()
    current_user = User.query.filter_by(name=current_user).first()
    todos = Todo.query.filter_by(user_id=current_user.id)
    todos = todos_schema.dump(todos)
    return jsonify(todos)


@app.route('/todo/<todo_id>', methods=['PUT'])
@jwt_required()
def update_a_todo(todo_id):
    try:
        current_user = get_jwt_identity()
        cuurent_user = User.query.filter_by(name=current_user).first()
        todo = Todo.query.filter_by(
            user_id=cuurent_user.id, id=todo_id).first()

        if not todo:
            return jsonify({'message': 'todo not found'}), 404

        data = request.get_json()
        todo = Todo.query.filter_by(
            user_id=cuurent_user.id, id=todo_id).update(data)

        db.session.commit()

        todo = Todo.query.filter_by(
            user_id=cuurent_user.id, id=todo_id).first()
        todo = todo_schema.dump(todo)

        return jsonify({'message': 'updated successfully', 'todo': todo})
    except (InvalidRequestError):
        return jsonify({'message': 'wrong keys passed'}), 400

@app.route('/todo/<todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user = get_jwt_identity()
    user = User.query.filter_by(name=user).first()
    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()

    if not todo:
        return jsonify({'message': 'todo not found'}), 404

    db.session.delete(todo)
    db.session.commit()
    todo = todo_schema.dump(todo)
    return jsonify({'message': 'deleted successfully', 'todo': todo}), 204