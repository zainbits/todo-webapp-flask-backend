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
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

user = Blueprint('user', __name__)

users_schema = UserSchema(many=True)
user_schema = UserSchema()

todos_schema = TodoSchema(many=True)
todo_schema = TodoSchema()


@user.route('/login')
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


@user.route('/about', methods=['GET'])
@jwt_required()
def about():
    current_user = get_jwt_identity()
    current_user = User.query.filter_by(name=current_user).first()
    user = user_schema.dump(current_user)
    return jsonify({'user': user}), 200


@user.route('/users', methods=['GET'])
@jwt_required()
@make_secure('admin')
def get_all_users():
    users = User.query.all()
    data = users_schema.dump(users)
    return jsonify(data)


@user.route('/user/<public_id>', methods=['GET'])
@jwt_required()
@make_secure('admin')
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message': 'no user found!'})

    data = user_schema.dump(user)
    return jsonify(data)


@user.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(uuid.uuid4()),
                    name=data['name'], password=hashed_password, admin=False)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as err:
        if "violates unique constraint" in str(err):
            return jsonify({"message": "Username is already taken"}), 409
    return jsonify({"message": "New user created"}), 201


@user.route('/admin/promote/<public_id>', methods=['PUT'])
@jwt_required()
@make_secure('admin')
def promote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "no user found"})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "user has been promoted to admin", "admin": user.admin})

@user.route('/admin/demote/<public_id>', methods=['PUT'])
@jwt_required()
@make_secure('admin')
def demote_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "no user found"})

    user.admin = False
    db.session.commit()

    return jsonify({"message": "user has been promoted to admin", "admin": user.admin})

@user.route('/admin/delete/<public_id>', methods=['DELETE'])
@jwt_required()
@make_secure('admin')
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "no user found"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "the user has been deleted"}), 200
