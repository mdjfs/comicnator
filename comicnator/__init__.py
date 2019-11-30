import csv
from flask import url_for
from flask_jsglue import JSGlue
from comicnator import database
from comicnator.comicnator import Comicnator
from comicnator.routes import bp


def create_app():
    app = Comicnator(__name__, instance_relative_config=True)
    jsglue = JSGlue(app)
    database.init_app(app)
    app.register_blueprint(bp)
    return app


app = create_app()


def reset():
    database.reset(inith(), initu())


def inith():
    urlheroes = url_for("static", filename="init/initheroes.csv")
    with open(urlheroes) as csvfile:
        read = csv.reader(csvfile, delimiter=",")
        dicc = {}
        i = 0
        for row in read:
            i += 1
            campos = []
            for field in row:
                campos.append(field)
            dicc[i] = campos
    return [dicc, i]


def initu():
    urluser = url_for("static", filename="init/inituser.csv")
    with open(urluser) as csvfile:
        read = csv.reader(csvfile, delimiter=",")
        dicc = {}
        i = 0
        for row in read:
            i += 1
            campos = []
            for field in row:
                campos.append(field)
            dicc[i] = campos
    return [dicc, i]
