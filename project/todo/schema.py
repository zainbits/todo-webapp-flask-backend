from marshmallow import fields
from project import ma


class TodoSchema(ma.Schema):
    id = fields.Integer()
    text = fields.String()
    complete = fields.Boolean()
    user_id = fields.Integer()
