import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from flask_login import login_user, login_required

# from comicnator.database import db, GameSessions

from comicnator.forms import learnForm

DEVICES = {
    "windows": "computer",
    "linux": "computer",
    "macos": "computer",
    "ipad": "computer",
    "iphone": "cellphone",
    "android": "cellphone",
}

bp = Blueprint("comicnator", __name__)


@bp.before_request
def before_request():
    if "device" not in session:
        session["device"] = DEVICES[request.user_agent.platform]


@bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@bp.route("/", methods=["GET", "POST"])
def index():
    if "redirecc" in request.form:
        return redirect(url_for("comicnator.interaccion"))
    if "go" in request.form:
        return redirect(url_for("comicnator.interaccion"))
    if session["device"] == "computer":
        return render_template("index.html")
    if session["device"] == "cellphone":
        return render_template("indexcell.html")
    return render_template("unsupported.html")


@bp.route("/start_game")
def start_game():
    session["session_id"] = current_app.start_game()
    return redirect(url_for("comicnator.interaccion"))


@bp.route("/inter", methods=["GET", "POST"])
def interaccion():
    if "final" in request.form:
        return redirect(url_for("comicnator.datos"))
    if not session.get("session_id") or "volver" in request.form:
        return redirect(url_for("comicnator.start_game"))
    pregunta, termino = current_app.interaccion(session["session_id"],
                                                request.form)
    if termino:
        del session["session_id"]
    if session["device"] == "computer":
        return render_template("inter.html", pregunta=pregunta, final=termino)
    if session["device"] == "cellphone":
        return render_template("intercell.html",
                               pregunta=pregunta,
                               final=termino)
    return render_template("unsupported.html")


@bp.route("/learn", methods=["GET", "POST"])
def datos():
    if request.method == "GET":
        if session["device"] == "computer":
            return render_template("form.html")
        if session["device"] == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")
    if request.method == "POST":
        if request.form.get("anzuelo") == "defecto":

            lista = [
                0,
                request.form.get("nombre"),
                request.form.get("genero"),
                request.form.get("origen"),
                request.form.get("comienzo"),
                request.form.get("capacidad"),
                request.form.get("descrip"),
            ]
            current_app.insertar_sugerencia(lista)
            success_message = "Gracias ! Un administrador"
            success_message += " verificara mi aprendizaje"
            flash(success_message)
            return redirect(url_for("comicnator.index"))
        if session["device"] == "computer":
            return render_template("form.html")
        if session["device"] == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")


@bp.route("/log-learn", methods=["GET", "POST"])
def login():
    if "username" not in session:
        loginform = learnForm(request.form)
        if request.method == "POST" and loginform.validate:
            username = loginform.username.data
            password = loginform.password.data
            success = current_app.verificacion(username, password)
            if success is not None:
                object_user = current_app.return_user(username, password)
                login_user(object_user)
                flash(success)
                session["username"] = username
                return redirect(url_for("comicnator.admin"))
        return render_template("login.html", form=loginform)
    else:
        return "Usted ya esta logueado"


@bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if "peticion" in session:
        if session["peticion"] == "":
            session.pop("peticion")
    if "peticion" not in session:
        lista = current_app.solicitar_sugerencia()
        llevar = ""
        j = 0
        if lista is not None:
            for i in lista:
                j += 1
                if j == len(lista):
                    llevar += "{}".format(i)
                else:
                    llevar += "{}.".format(i)
        session["peticion"] = llevar
    sugerencia = session["peticion"]
    if request.method == "POST":
        if "acepto" in request.form:
            sugerencia = session["peticion"]
            lista = sugerencia.split(".")
            current_app.insertar(lista)
            current_app.borrar_sugerencia()
            session.pop("peticion")
            return redirect(url_for("comicnator.admin"))
        if "deniego" in request.form:
            current_app.borrar_sugerencia()
            session.pop("peticion")
            return redirect(url_for("comicnator.admin"))
    return render_template("admin.html", query=sugerencia)
