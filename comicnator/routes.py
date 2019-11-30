from flask import Blueprint


def create_blueprint():
    bp = Blueprint("comicnator", __name__)
    return bp


bp = create_blueprint()
