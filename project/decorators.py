import functools

from flask import jsonify
from flask_jwt_extended import get_jwt_identity

from project.user.models import User


def make_secure(access_level):
    # access_level will be used in future versions
    # if current_user.access_level == access_level:
    #     TODO: give or deny access
    def decorator(func):
        @functools.wraps(func)
        def secure_function(*args, **kwargs):
            current_user = get_jwt_identity()
            current_user = User.query.filter_by(name=current_user).first()
            if not current_user.admin:
                return jsonify({'msg': 'permission denied'})
            else:
                return func(*args, **kwargs)
        return secure_function
    return decorator
