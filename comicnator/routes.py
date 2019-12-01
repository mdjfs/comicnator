import os
from comicnator import form
from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
    Blueprint,
    json,
    jsonify
)
import comicnator


def create_blueprint():
    bp = Blueprint("bp", __name__)
    return bp


bp = create_blueprint()


@bp.route("/hardreset")
def reset():
    if "username" in session:
        dataheroe = comicnator.inith()
        datauser = comicnator.initu()
        comicnator.database.reset(dataheroe, datauser)
        return "Listo!"
    else:
        return "No esta logueado."


@bp.route('/prueba')
def prueba():
    return "Esto es una prueba!"


@bp.before_request
def reconoce():
    comicnator.app.mapeo()
    comicnator.app.reconocer(request.user_agent.platform)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if "redirecc" in request.form:
        return redirect(url_for("bp.interaccion"))
    if "go" in request.form:
        return redirect(url_for("bp.interaccion"))
    if comicnator.app.device == "computer":
        return render_template("index.html")
    if comicnator.app.device == "cellphone":
        return render_template("indexcell.html")
    return render_template("unsupported.html")


@bp.route("/favicon.ico")
def favicon():
    return send_from_directory(
                os.path.join(comicnator.app.root_path, "static"),
                "favicon.ico",
                mimetype="image/vnd.microsoft.icon",
                )


@bp.route("/pruebajson", methods=["POST"])
def pruebajson():
    data = request.get_json()
    print(data['exclusion'])
    return jsonify(status="success", data=data)


@bp.route("/hola")
def jsonify():
    return render_template("json.html")


@bp.route("/inter", methods=["GET", "POST"])
def interaccion():
    if "volver" in request.form:
        return redirect(url_for("bp.interaccion"))
    if "final" in request.form:
        return redirect(url_for("bp.datos"))
    lista = comicnator.app.interaccion(request.method, session, request.form)
    q = lista[1]
    termino = lista[2]
    if termino is False:
        req = lista[0]
        session["exclusion_fila"] = req["exclusion_fila"]
        session["exclusion_columna"] = req["exclusion_columna"]
        session["probable"] = req["probable"]
        session["posicion"] = req["posicion"]
        session["incert"] = req["incert"]
        session["adivino"] = req["adivino"]
    else:
        session.clear()
    if comicnator.app.device == "computer":
        return render_template("inter.html", pregunta=q, final=termino)
    if comicnator.app.device == "cellphone":
        return render_template("intercell.html", pregunta=q, final=termino)
    return render_template("unsupported.html")


@bp.route("/learn", methods=["GET", "POST"])
def datos():
    if request.method == "GET":
        if comicnator.app.device == "computer":
            return render_template("form.html")
        if comicnator.app.device == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")
    if request.method == "POST":
        if request.form.get("anzuelo") == "defecto":

            lista = [0, request.form.get("nombre"),
                     request.form.get("genero"),
                     request.form.get("origen"),
                     request.form.get("comienzo"),
                     request.form.get("capacidad"),
                     request.form.get("descrip")]
            comicnator.app.InsertarSugerencia(lista)
            success_message = "Gracias ! Un administrador"
            success_message += " verificara mi aprendizaje"
            flash(success_message)
            return redirect(url_for("bp.index"))
        if comicnator.app.device == "computer":
            return render_template("form.html")
        if comicnator.app.device == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")


@bp.route("/log-learn", methods=["GET", "POST"])
def Login():
    if "username" not in session:
        loginform = form.learnForm(request.form)
        if request.method == "POST" and loginform.validate:
            username = loginform.username.data
            password = loginform.password.data
            success = comicnator.app.Verificacion(username, password)
            if success is not None:
                flash(success)
                session["username"] = username
                return redirect(url_for("bp.admin"))
        return render_template("login.html", form=loginform)
    else:
        return "Usted ya esta logueado"


@bp.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" in session:
        if "peticion" not in session:
            lista = comicnator.app.SolicitarSugerencia()
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
                comicnator.app.Insertar(lista)
                comicnator.app.BorrarSugerencia()
                del session["peticion"]
                return redirect(url_for("bp.admin"))
            if "deniego" in request.form:
                comicnator.app.BorrarSugerencia()
                del session["peticion"]
                return redirect(url_for("bp.admin"))
        return render_template("admin.html", query=sugerencia)
    else:
        return "No esta logueado."
