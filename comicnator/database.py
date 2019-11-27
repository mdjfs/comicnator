from werkzeug.security import check_password_hash, generate_password_hash

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(94))

    def __init__(self, username, password):
        self.username = username
        self.password = self.encryption(password)

    def encryption(self, password):
        return generate_password_hash(password)

    def verify(self, password):
        return check_password_hash(self.password, password)
