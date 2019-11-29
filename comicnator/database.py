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


class HeroesMarvel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    genero = db.Column('es de genero', db.String, nullable=False)
    origen = db.Column('es de origen', db.String, nullable=False)
    empezo = db.Column('empezo con', db.String, nullable=False)
    capacidad = db.Column('tiene como capacidad especial',
                          db.String,
                          nullable=False)
    describe = db.Column('se describe como', db.String, nullable=False)
    __table_args__ = (db.UniqueConstraint(
                        'es de genero',
                        'es de origen',
                        'empezo con',
                        'tiene como capacidad especial',
                        'se describe como'),)
