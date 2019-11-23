import os

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from sqlalchemy import create_engine, inspect

from comicnator import form
from comicnator.config import DevelopmentConfig
from comicnator.interaccion import Seleccion
from comicnator.models import User
from flask_jsglue import JSGlue

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
jsglue = JSGlue(app)

address = "postgresql://marcos:Golf45@localhost:5432/ComicNator"
engine = create_engine(address)
inspector = inspect(engine)


def CountRow():
    r = engine.execute("SELECT COUNT(*) FROM heroes")
    a = r.fetchone()
    return a[0]


def CountColumn():
    query = "SELECT COUNT (*) as conteo FROM information_schema.columns"
    query += " WHERE table_schema = 'public' AND table_name = 'heroes'"
    r = engine.execute(query)
    a = r.fetchone()
    return a[0]


rownumber = CountRow()
columnumber = CountColumn()


def detect():
    device = None
    platform = request.user_agent.platform
    if (
        platform == "windows"
        or platform == "linux"
        or platform == "macos"
        or platform == "ipad"
    ):
        device = "computer"

    if platform == "iphone" or platform == "android":
        device = "cellphone"
    return device


@app.route("/", methods=["GET", "POST"])
def index():
    if "redirecc" in request.form:
        return redirect(url_for("interaccion"))
    if "go" in request.form:
        return redirect(url_for("interaccion"))
    device = detect()
    if device == "computer":
        return render_template("index.html")
    if device == "cellphone":
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
    if request.method == "GET":
        if "posicion" in session:
            pass
        else:
            session["exclusion_fila"] = []
            session["exclusion_fila"] = fillarray(
                session["exclusion_fila"], rownumber, False
            )
            session["exclusion_columna"] = []
            session["exclusion_columna"] = fillarray(
                session["exclusion_columna"], columnumber, False
            )
            session["probable"] = []
            session["probable"] = fillarray(session["probable"], rownumber, 0.0)
            session["posicion"] = []
            session["incert"] = False
            session["posicion"] = Seleccion(
                session["exclusion_fila"],
                session["exclusion_columna"],
                session["incert"],
                [rownumber, columnumber],
            )
            session["adivino"] = False
        finish = isfinal(session["probable"])
        if finish is True:
            session["incert"] = HabilitarIncertidumbre(
                session["exclusion_columna"], session["probable"]
            )
            if session["incert"] is True:
                session["probable"] = Quitarprob(session["probable"])
                finish = False
        ver = VerificarExclusion(session["exclusion_columna"])
        if finish is False:
            if session["posicion"] is not None:
                q = Init(session)
            elif session["posicion"] is None or ver:
                q = "No pudimos encontrar tu personaje"
                session["adivino"] = True
        else:
            if finish is True:
                q = getperson(session["probable"])
                if q is not None:
                    session["adivino"] = True
                else:
                    if session["posicion"] is None or ver:
                        q = Init(session)
                    else:
                        q = "No pudimos encontrar tu personaje"
                        session["adivino"] = True
        estado = False
        estado = session["adivino"]
        if estado is True:
            session.clear()
        device = detect()
        if device == "computer":
            return render_template("inter.html", pregunta=q, final=estado)
        if device == "cellphone":
            return render_template("intercell.html", pregunta=q, final=estado)
        return render_template("unsupported.html")
    if request.method == "POST":
        if "volver" in request.form:
            return redirect(url_for("interaccion"))
        if "final" in request.form:
            return redirect(url_for("datos"))
        if "posicion" in session:
            if "si" in request.form:
                exc = exclusion(session, True)
                prb = Probabilidad(session, True)
                session["exclusion_fila"] = exc["exclusion_fila"]
                session["exclusion_columna"] = exc["exclusion_columna"]
                session["probable"] = prb["probable"]
            if "no" in request.form:
                exc = exclusion(session, False)
                prb = Probabilidad(session, False)
                session["exclusion_fila"] = exc["exclusion_fila"]
                session["exclusion_columna"] = exc["exclusion_columna"]
                session["probable"] = prb["probable"]
            if "no lo se" in request.form:
                pass
            finish = isfinal(session["probable"])
            if finish is True:
                session["incert"] = HabilitarIncertidumbre(
                    session["exclusion_columna"], session["probable"]
                )
                if session["incert"] is True:
                    session["probable"] = Quitarprob(session["probable"])
                    print(session["probable"])
                    finish = False
            session["posicion"] = Seleccion(
                session["exclusion_fila"],
                session["exclusion_columna"],
                session["incert"],
                [rownumber, columnumber],
            )
            ver = VerificarExclusion(session["exclusion_columna"])
            if finish is False:
                if session["posicion"] is not None:
                    q = Init(session)
                elif session["posicion"] is None or ver:
                    q = "No pudimos encontrar tu personaje"
                    session["adivino"] = True
            else:
                if finish is True:
                    q = getperson(session["probable"])
                    if q is not None:
                        session["adivino"] = True
                    else:
                        if session["posicion"] is None or ver:
                            q = Init(session)
                        else:
                            q = "No pudimos encontrar tu personaje"
                            session["adivino"] = True
            estado = False
            estado = session["adivino"]
            if estado is True:
                session.clear()
            device = detect()
            if device == "computer":
                return render_template("inter.html", pregunta=q, final=estado)
            if device == "cellphone":
                return render_template("intercell.html", pregunta=q, final=estado)
            return render_template("unsupported.html")


@app.route("/learn", methods=["GET", "POST"])
def datos():
    device = detect()
    if request.method == "GET":
        if device == "computer":
            return render_template("form.html")
        if device == "cellphone":
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
            engine.execute(query)
            success_message = "Gracias ! Un administrador"
            success_message += " verificara mi aprendizaje"
            flash(success_message)
            return redirect(url_for("index"))
        if device == "computer":
            return render_template("form.html")
        if device == "cellphone":
            return render_template("learncell.html")
        return render_template("unsupported.html")


@app.route("/log-learn", methods=["GET", "POST"])
def Login():
    if "username" not in session:
        loginform = form.learnForm(request.form)
        if request.method == "POST" and loginform.validate:
            username = loginform.username.data
            password = loginform.password.data
            user = User.query.filter_by(username=username).first()
            if user is not None and user.verify(password):
                success_message = "Bienvenido " + username
                flash(success_message)
                session["username"] = username
                return redirect(url_for("admin"))
        return render_template("login.html", form=loginform)
    else:
        return "Usted ya esta logueado"


def Init(data):
    pregunta = Question(data["posicion"])
    return pregunta


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "username" in session:
        if "peticion" not in session:
            x = engine.execute("SELECT *FROM heroes_learn")
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
                engine.execute(query)
                query = "delete from heroes_learn where "
                query += "id_heroes_learn={}".format(lista[0])
                engine.execute(query)
                del session["peticion"]
                return redirect(url_for("admin"))
            if "deniego" in request.form:
                sugerencia = session["peticion"]
                lista = sugerencia.split(".")
                query = "delete from heroes_learn where "
                query += "id_heroes_learn={}".format(lista[0])
                engine.execute(query)
                del session["peticion"]
                return redirect(url_for("admin"))
        return render_template("admin.html", query=sugerencia)
    else:
        return "No esta logueado."


def Question(pos):
    filtro = inspector.get_columns("heroes")
    dicc = filtro[pos[0]]
    columna = dicc["name"]
    r = engine.execute('SELECT "' + dicc["name"] + '" from heroes')
    i = 0
    rowfilter = ""
    for row in r:
        i += 1
        if i == pos[1]:
            rowfilter = row[0]
    fila = rowfilter
    return "Su personaje " + columna + " " + fila


def fillarray(array, iterator, valor):
    for i in range(iterator + 1):
        array.append(valor)
    return array


def exclusion(data, mode):
    filtro = inspector.get_columns("heroes")
    pos = data["posicion"]
    exclusion_fila = data["exclusion_fila"]
    exclusion_columna = data["exclusion_columna"]
    dicc = filtro[pos[0]]
    r = engine.execute('SELECT "' + dicc["name"] + '" from heroes')
    if mode is True:
        exclusion_columna[pos[0]] = True
        rowfilter = ""
        i = 0
        for row in r:
            i += 1
            if i == pos[1]:
                rowfilter = row[0]
        i = 0
        r = engine.execute('SELECT "' + dicc["name"] + '" from heroes')
        for row in r:
            i += 1
            if row[0] != rowfilter:
                exclusion_fila[i] = True
    else:
        rowfilter = ""
        i = 0
        for row in r:
            i += 1
            if i == pos[1]:
                rowfilter = row[0]
        i = 0
        r = engine.execute('SELECT "' + dicc["name"] + '" from heroes')
        for row in r:
            i += 1
            if row[0] == rowfilter:
                exclusion_fila[i] = True
    data["exclusion_fila"] = exclusion_fila
    data["exclusion_columna"] = exclusion_columna
    return data


def VerificarExclusion(exclusion_columna):
    j = 0
    for i in exclusion_columna:
        if i is True:
            j += 1
    if j == 4:
        return True
    else:
        return False


def HabilitarIncertidumbre(exclusion_columna, prob):
    j = 0
    excluidos_todos = False
    repetidos = False
    for i in exclusion_columna:
        if i is True:
            j += 1
    if j == 3:
        excluidos_todos = True
    else:
        excluidos_todos = False
    j = 0
    for p in prob:
        if p > 100:
            j += 1
    if j > 1:
        repetidos = True
    return repetidos or excluidos_todos


def Quitarprob(prob):
    j = 5
    while j > 1:
        j = 0
        for i in range(len(prob)):
            if prob[i] > 100:
                prob[i] -= 20
                j += 1
    return prob


def Probabilidad(data, mode):
    filtro = inspector.get_columns("heroes")
    pos = data["posicion"]
    probabilidad = data["probable"]
    repitio = []
    repitio = fillarray(repitio, len(probabilidad) - 1, False)
    dicc = filtro[pos[0]]
    r = engine.execute('SELECT "' + dicc["name"] + '" from heroes')
    rowfilter = ""
    i = 0
    for row in r:
        i += 1
        if i == pos[1]:
            rowfilter = row[0]
    i = 0
    repetido = 0
    r = engine.execute('SELECT "' + dicc["name"] + '" from heroes')
    for row in r:
        i += 1
        if row[0] == rowfilter:
            repetido += 1
            repitio[i] = True
    filas = rownumber
    prob = repetido / filas * 100
    if mode is True:
        for x in range(filas):
            if repitio[x] is True and x != 0:
                if prob < 10:
                    probabilidad[x] += 80
                if prob > 10 and prob < 30:
                    probabilidad[x] += 60
                if prob > 30 and prob < 60:
                    probabilidad[x] += 40
                if prob > 60 and prob < 100:
                    probabilidad[x] += 15
    else:
        for x in range(filas):
            if repitio[x] is False and x != 0:
                if prob > 50:
                    probabilidad[x] += 80
                if prob > 20 and prob < 50:
                    probabilidad[x] += 40
                if prob < 20:
                    probabilidad[x] += 10
    data["probable"] = probabilidad
    return data


def isfinal(prob):
    for p in prob:
        if p > 100:
            return True
    return False


def getperson(prob):
    i = 0
    its = 1
    paso = False
    for p in prob:
        if p > 100:
            its = i
            paso = True
            break
        i += 1
    r = engine.execute("SELECT nombre_heroes from heroes")
    rowfilter = ""
    i = 1
    for row in r:
        if i == its:
            rowfilter = row[0]
        i += 1
    if paso is False:
        return None
    return "Su personaje es " + rowfilter
