from marshmallow import fields
from project import ma


class UserSchema(ma.Schema):
    id = fields.Integer()
    public_id = fields.String()
    name = fields.String()
    password = fields.String()
    admin = fields.Boolean()
