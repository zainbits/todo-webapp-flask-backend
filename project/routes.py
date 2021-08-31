import uuid
import datetime

from project import app, db
from project.decorators import make_secure
from project.user.models import User
from project.user.schema import UserSchema
from project.todo.models import Todo

from flask import request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

users_schema = UserSchema(many=True)
user_schema = UserSchema()


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
        return make_response({'message':'Could not verify'},  401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response({'message':'Could not verify'},  401, {'WWW-Authenticate': 'Basic realm="Login required"'})

    if check_password_hash(user.password, auth.password):
        token = create_access_token(identity=user.name, expires_delta=datetime.timedelta(seconds=10))
        return jsonify({'token': token})

    return make_response({'message':'Could not verify'},  401, {'WWW-Authenticate': 'Basic realm="Login required"'})


@app.route('/about', methods=['GET'])
@jwt_required()
def about():
    current_user = get_jwt_identity()
    current_user = User.query.filter_by(name=current_user).first()
    return jsonify({'user': current_user.admin}), 200


@app.route('/todo', methods=['POST'])
def create_todo():
    data = request.get_json()
    current_user = get_jwt_identity()
    current_user = User.query.filter_by(name=current_user)
    new_todo = Todo(text=data['text'], complete=False, user_id=current_user.id)
    db.session.add(new_todo)
    db.session.commit()

    return jsonify({'msg': 'TODO Created'})
