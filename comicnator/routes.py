from flask import Blueprint
from comicnator import reconoce


def create_blueprint():
    bp = Blueprint("comicnator", __name__)
    return bp


bp = create_blueprint()
bp.before_request(reconoce())
