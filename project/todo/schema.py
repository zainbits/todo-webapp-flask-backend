from project import ma
from marshmallow import fields

class TodoSchema(ma.Schema):
    id = fields.Integer()
    text = fields.String()
    complete = fields.Boolean()
    user_id = fields.Integer()
