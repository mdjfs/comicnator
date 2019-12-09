from csv import DictReader
from datetime import datetime
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

login = LoginManager()
db = SQLAlchemy(
    session_options={"autoflush": False, "autocommit": False, "expire_on_commit": False}
)


def init_app(app):
    db.init_app(app)
    login.init_app(app)
    app.cli.add_command(init_db_command)
    app.cli.add_command(easter_egg)


@login.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@click.command("easteregg")
@with_appcontext
def easter_egg():
    """ Wow, how do you find this ?? """
    print("hola.. je je")


@click.command("reset-db")
@with_appcontext
def init_db_command():
    """Installs or purges the db"""
    db.drop_all()
    db.create_all()
    for table in (User, HeroesMarvel):
        init_file = Path(
            current_app.root_path, "initialization_data", f"{table.__tablename__}.csv"
        )
        with open(init_file) as file:
            reader = DictReader(file)
            for row in reader:
                db.session.add(table(**row))
    db.session.commit()
    click.echo("Initialized the db.")


class User(db.Model, UserMixin):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(94))

    def __init__(self, *args, **kwargs):
        if "password" in kwargs:
            kwargs["password"] = self.encryption(kwargs["password"])
        super().__init__(*args, **kwargs)

    def encryption(self, password):
        return generate_password_hash(password)

    def verify(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.username}>"


class HeroesMarvel(db.Model):
    __tablename__ = "HeroesMarvel"
    __table_args__ = (
        db.UniqueConstraint(
            "es de genero",
            "es de origen",
            "empezo con",
            "tiene como capacidad especial",
            "se describe como",
        ),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)
    genero = db.Column("es de genero", db.String, nullable=False)
    origen = db.Column("es de origen", db.String, nullable=False)
    empezo = db.Column("empezo con", db.String, nullable=False)
    capacidad = db.Column("tiene como capacidad especial", db.String, nullable=False)
    describe = db.Column("se describe como", db.String, nullable=False)

    def __repr__(self):
        return f"<Heroe {self.nombre}>"


class MarvelSugerencias(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String, nullable=False)
    genero = db.Column("es de genero", db.String, nullable=False)
    origen = db.Column("es de origen", db.String, nullable=False)
    empezo = db.Column("empezo con", db.String, nullable=False)
    capacidad = db.Column("tiene como capacidad especial", db.String, nullable=False)
    describe = db.Column("se describe como", db.String, nullable=False)
    __table_args__ = (
        db.UniqueConstraint(
            "es de genero",
            "es de origen",
            "empezo con",
            "tiene como capacidad especial",
            "se describe como",
        ),
    )

    def __repr__(self):
        return f"<MarvelSugerencias sobre {self.nombre}>"


class GameSessions(db.Model):
    """List of current user sessions"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    creation_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("User.id"), nullable=True)
    user = db.relationship("User", backref="sessions")
    incert = db.Column(db.Boolean)
    adivino = db.Column(db.Boolean)
    _exclusion_fila = db.Column("exclusion_fila", db.String)
    _exclusion_columna = db.Column("exclusion_columna", db.String)
    _probable = db.Column("probable", db.String)
    _posicion = db.Column("posicion", db.String)

    @property
    def exclusion_fila(self):
        return tuple((bool(int(i)) for i in self._exclusion_fila.split()))

    @exclusion_fila.setter
    def exclusion_fila(self, val):
        self._exclusion_fila = " ".join(("1" if i else "0" for i in val))

    @property
    def exclusion_columna(self):
        return tuple((bool(int(i)) for i in self._exclusion_columna.split()))

    @exclusion_columna.setter
    def exclusion_columna(self, val):
        self._exclusion_columna = " ".join(("1" if i else "0" for i in val))

    @property
    def probable(self):
        if self._probable == "None":
            return None
        return tuple((float(i) for i in self._probable.split()))

    @probable.setter
    def probable(self, val):
        if val is None:
            self._probable = "None"
        else:
            self._probable = " ".join((str(i) for i in val))

    @property
    def posicion(self):
        if self._posicion == "None":
            return None
        return tuple((int(i) for i in self._posicion.split()))

    @posicion.setter
    def posicion(self, val):
        if val is None:
            self._posicion = "None"
        else:
            self._posicion = " ".join((str(i) for i in val))

    @property
    def is_final(self):
        for p in self.probable:
            if p > 100:
                return True
        return False

    def __repr__(self):
        return f"<Session {self.id}>"
