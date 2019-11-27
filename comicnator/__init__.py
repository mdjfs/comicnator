import os

from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_jsglue import JSGlue

from comicnator import form
from comicnator import database

from comicnator.comicnator import Comicnator


def create_app():
    app = Comicnator(__name__, instance_relative_config=True)
    jsglue = JSGlue(app)
    database.init_app(app)
    return app


app = create_app()


@app.route("/", methods=["GET", "POST"])
def index():
    app.reconocer(request.user_agent.platform)
    if "redirecc" in request.form:
        return redirect(url_for("interaccion"))
    if "go" in request.form:
        return redirect(url_for("interaccion"))
    if app.device == "computer":
        return render_template("index.html")
    if app.device == "cellphone":
        return render_template("indexcell.html")
    return render_template("unsupported.html")


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
                os.path.join(app.root_path, "static"),
                "favicon.ico",
                mimetype="image/vnd.microsoft.icon",
                )


@app.route("/inter", methods=["GET", "POST"])
def interaccion():
    if "volver" in request.form:
        return redirect(url_for("interaccion"))
    if "final" in request.form:
        return redirect(url_for("datos"))
    lista = app.interaccion(request.method, session, request.form)
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
    if app.device == "computer":
        return render_template("inter.html", pregunta=q, final=termino)
    if app.device == "cellphone":
        return render_template("intercell.html", pregunta=q, final=termino)
    return render_template("unsupported.html")


@app.route("/learn", methods=["GET", "POST"])
def datos():
    if request.method == "GET":
        if app.device == "computer":
            return render_template("form.html")
        if app.device == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")
    if request.method == "POST":
        if request.form.get("anzuelo") == "defecto":
            query = "INSERT INTO heroes_learn "
            query += "(nombre_heroes_learn,"
            query += "'es de genero',"
            query += "'es de origen',"
            query += "'empezo con',"
            query += "'tiene como capacidad especial',"
            query += "'se describe como') VALUES"
            query = query.replace("'", '"')
            query += "('" + request.form.get("nombre") + "','"
            query += request.form.get("genero") + "','"
            query += request.form.get("origen") + "','"
            query += request.form.get("comienzo") + "','"
            query += request.form.get("capacidad") + "','"
            query += request.form.get("descrip") + "')"
            app.engine.execute(query)
            success_message = "Gracias ! Un administrador"
            success_message += " verificara mi aprendizaje"
            flash(success_message)
            return redirect(url_for("index"))
        if app.device == "computer":
            return render_template("form.html")
        if app.device == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")


@app.route("/log-learn", methods=["GET", "POST"])
def Login():
    if "username" not in session:
        loginform = form.learnForm(request.form)
        if request.method == "POST" and loginform.validate:
            username = loginform.username.data
            password = loginform.password.data
            user = database.User.query.filter_by(username=username).first()
            if user is not None and user.verify(password):
                success_message = "Bienvenido " + username
                flash(success_message)
                session["username"] = username
                return redirect(url_for("admin"))
        return render_template("login.html", form=loginform)
    else:
        return "Usted ya esta logueado"


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" in session:
        if "peticion" not in session:
            x = app.engine.execute("SELECT *FROM heroes_learn")
            lista = x.fetchone()
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
                query = "INSERT INTO heroes "
                query += "(nombre_heroes,"
                query += "'es de genero',"
                query += "'es de origen',"
                query += "'empezo con',"
                query += "'tiene como capacidad especial',"
                query += "'se describe como') VALUES"
                query = query.replace("'", '"')
                query += "('" + lista[1] + "','"
                query += lista[2] + "','"
                query += lista[3] + "','"
                query += lista[4] + "','"
                query += lista[5] + "','"
                query += lista[6] + "')"
                app.engine.execute(query)
                query = "delete from heroes_learn where "
                query += "id_heroes_learn={}".format(lista[0])
                app.engine.execute(query)
                del session["peticion"]
                return redirect(url_for("admin"))
            if "deniego" in request.form:
                sugerencia = session["peticion"]
                lista = sugerencia.split(".")
                query = "delete from heroes_learn where "
                query += "id_heroes_learn={}".format(lista[0])
                app.engine.execute(query)
                del session["peticion"]
                return redirect(url_for("admin"))
        return render_template("admin.html", query=sugerencia)
    else:
        return "No esta logueado."
