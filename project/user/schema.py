from project import ma
from marshmallow import fields


class UserSchema(ma.Schema):
    id = fields.Integer()
    public_id = fields.String()
    name = fields.String()
    password = fields.String()
    admin = fields.Boolean()
