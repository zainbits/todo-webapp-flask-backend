from project import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(255))
    admin = db.Column(db.Boolean)

    def __repr__(self):
        return self.name
