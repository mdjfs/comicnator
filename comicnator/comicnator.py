from flask import Flask
from sqlalchemy import create_engine, inspect
import random


class Comicnator(Flask):
    """ Clase que contiene todos los metodos de la Aplicacion """

    def __init__(self, *args, **kwargs):
        """ Metodo init que tiene las variables a usar en la
        Aplicacion """
        Flask.__init__(self, *args, **kwargs)
        self.config.from_pyfile("config.py")
        self.engine = create_engine(
            self.config["SQLALCHEMY_DATABASE_URI"]
        )
        self.inspector = inspect(self.engine)
        self.rownumber = self.countRow()
        self.columnumber = self.countColumn()

    def reconocer(self, platform):
        self.device = self.detect(platform)

    def countRow(self):
        """ Metodo que se encarga de contar las Filas
        de la tabla heroes """
        r = self.engine.execute("SELECT COUNT(*) FROM heroes")
        a = r.fetchone()
        return a[0]

    def countColumn(self):
        """ Metodo que se encarga de Contar las columnas
        de la tabla heroes """
        query = "SELECT COUNT (*) as conteo FROM information_schema.columns"
        query += " WHERE table_schema = 'public' AND table_name = 'heroes'"
        r = self.engine.execute(query)
        a = r.fetchone()
        return a[0]

    def detect(self, platform):
        """ Metodo que se encarga de detectar el dispositivo """
        device = None
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

    def interaccion(self, method, session, form):
        """ El metodo mas grueso de lo grueso, es decir,
        xD, se encarga de manejar todo lo que son las preguntas
        y respuestas """
        if method == "GET":
            if "posicion" in session:
                pass
            else:
                session["exclusion_fila"] = []
                session["exclusion_fila"] = self.fillarray(
                                            session["exclusion_fila"],
                                            self.rownumber,
                                            False)
                session["exclusion_columna"] = []
                session["exclusion_columna"] = self.fillarray(
                                               session["exclusion_columna"],
                                               self.columnumber,
                                               False)
                session["probable"] = []
                session["probable"] = self.fillarray(
                                      session["probable"],
                                      self.rownumber,
                                      0.0)
                session["posicion"] = []
                session["incert"] = False
                session["posicion"] = self.Seleccion(
                                      session["exclusion_fila"],
                                      session["exclusion_columna"],
                                      session["incert"],
                                      [self.rownumber, self.columnumber])
                session["adivino"] = False
            finish = self.isfinal(session["probable"])
            if finish is True:
                session["incert"] = self.HabilitarIncertidumbre(
                                    session["exclusion_columna"],
                                    session["probable"])
                if session["incert"] is True:
                    session["probable"] = self.Quitarprob(
                                          session["probable"])
                    finish = False
            ver = self.VerificarExclusion(
                  session["exclusion_columna"])
            if finish is False:
                if session["posicion"] is not None:
                    q = self.Init(session)
                elif session["posicion"] is None or ver:
                    q = "No pudimos encontrar tu personaje"
                    session["adivino"] = True
            else:
                if finish is True:
                    q = self.getperson(session["probable"])
                    if q is not None:
                        session["adivino"] = True
                    else:
                        if session["posicion"] is None or ver:
                            q = self.Init(session)
                        else:
                            q = "No pudimos encontrar tu personaje"
                            session["adivino"] = True
            estado = False
            estado = session["adivino"]
            if estado is True:
                session.clear()
            return [session, q, estado]
        if method == "POST":
            if "posicion" in session:
                if "si" in form:
                    exc = self.exclusion(session, True)
                    prb = self.Probabilidad(session, True)
                    session["exclusion_fila"] = exc["exclusion_fila"]
                    session["exclusion_columna"] = exc["exclusion_columna"]
                    session["probable"] = prb["probable"]
                if "no" in form:
                    exc = self.exclusion(session, False)
                    prb = self.Probabilidad(session, False)
                    session["exclusion_fila"] = exc["exclusion_fila"]
                    session["exclusion_columna"] = exc["exclusion_columna"]
                    session["probable"] = prb["probable"]
                if "no lo se" in form:
                    pass
                finish = self.isfinal(session["probable"])
                if finish is True:
                    session["incert"] = self.HabilitarIncertidumbre(
                                        session["exclusion_columna"],
                                        session["probable"])
                    if session["incert"] is True:
                        session["probable"] = self.Quitarprob(
                                              session["probable"])
                        finish = False
                session["posicion"] = self.Seleccion(
                                      session["exclusion_fila"],
                                      session["exclusion_columna"],
                                      session["incert"],
                                      [self.rownumber, self.columnumber])
                ver = self.VerificarExclusion(session["exclusion_columna"])
                if finish is False:
                    if session["posicion"] is not None:
                        q = self.Init(session)
                    elif session["posicion"] is None or ver:
                        q = "No pudimos encontrar tu personaje"
                        session["adivino"] = True
                else:
                    if finish is True:
                        q = self.getperson(session["probable"])
                        if q is not None:
                            session["adivino"] = True
                    else:
                        if session["posicion"] is None or ver:
                            q = self.Init(session)
                        else:
                            q = "No pudimos encontrar tu personaje"
                            session["adivino"] = True
                estado = False
                estado = session["adivino"]
                if estado is True:
                    session.clear()
                return [session, q, estado]

    def Init(self, data):
        """Metodo que se encarga de devolver la pregunta de la
        posicion en que se encuentra el usuario """
        pregunta = self.Question(data["posicion"])
        return pregunta

    def Question(self, pos):
        """Metodo que se encarga de buscar en la base de datos
        la posicion en que se encuentra el usuario"""
        filtro = self.inspector.get_columns("heroes")
        dicc = filtro[pos[0]]
        columna = dicc["name"]
        r = self.engine.execute('SELECT "' + dicc["name"] + '" from heroes')
        i = 0
        rowfilter = ""
        for row in r:
            i += 1
            if i == pos[1]:
                rowfilter = row[0]
        fila = rowfilter
        return "Su personaje " + columna + " " + fila

    def fillarray(self, array, iterator, valor):
        """Como su nombre lo dice, el metodo llena un array"""
        for i in range(iterator + 1):
            array.append(valor)
        return array

    def exclusion(self, data, mode):
        """Metodo que se encarga de excluir personajes
        para que no salgan preguntas que no tengan que ver"""
        filtro = self.inspector.get_columns("heroes")
        pos = data["posicion"]
        exclusion_fila = data["exclusion_fila"]
        exclusion_columna = data["exclusion_columna"]
        dicc = filtro[pos[0]]
        r = self.engine.execute('SELECT "' + dicc["name"] + '" from heroes')
        if mode is True:
            exclusion_columna[pos[0]] = True
            rowfilter = ""
            i = 0
            for row in r:
                i += 1
                if i == pos[1]:
                    rowfilter = row[0]
            i = 0
            name = dicc["name"]
            r = self.engine.execute('SELECT "' + name + '" from heroes')
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
            name = dicc["name"]
            r = self.engine.execute('SELECT "' + name + '" from heroes')
            for row in r:
                i += 1
                if row[0] == rowfilter:
                    exclusion_fila[i] = True
        data["exclusion_fila"] = exclusion_fila
        data["exclusion_columna"] = exclusion_columna
        return data

    def VerificarExclusion(self, exclusion_columna):
        """Metodo que se encarga de verificar si todo no
        esta excluido"""
        j = 0
        for i in exclusion_columna:
            if i is True:
                j += 1
        if j == 4:
            return True
        else:
            return False

    def HabilitarIncertidumbre(self, exclusion_columna, prob):
        """Metodo que habilita preguntas especificas si las
        basicas  ya se hicieron todas"""
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

    def Quitarprob(self, prob):
        """Este metodo si encuentra una probabilidad mayor de 100, la baja
        hasta que quede en menos de 100"""
        j = 5
        while j > 1:
            j = 0
            for i in range(len(prob)):
                if prob[i] > 100:
                    prob[i] -= 20
                    j += 1
        return prob

    def Probabilidad(self, data, mode):
        """Este metodo da probabilidades a unos personajes
        u otros dependiendo la respuesta"""
        filtro = self.inspector.get_columns("heroes")
        pos = data["posicion"]
        probabilidad = data["probable"]
        repitio = []
        repitio = self.fillarray(repitio, len(probabilidad) - 1, False)
        dicc = filtro[pos[0]]
        r = self.engine.execute('SELECT "' + dicc["name"] + '" from heroes')
        rowfilter = ""
        i = 0
        for row in r:
            i += 1
            if i == pos[1]:
                rowfilter = row[0]
        i = 0
        repetido = 0
        r = self.engine.execute('SELECT "' + dicc["name"] + '" from heroes')
        for row in r:
            i += 1
            if row[0] == rowfilter:
                repetido += 1
                repitio[i] = True
        filas = self.rownumber
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

    def isfinal(self, prob):
        """Como su nombre lo dice,
        si hay una probabilidad mayor a 100,
        es probable que ya haya adivinado"""
        for p in prob:
            if p > 100:
                return True
        return False

    def getperson(self, prob):
        """Obtiene el nombre del personaje"""
        i = 0
        its = 1
        paso = False
        for p in prob:
            if p > 100:
                its = i
                paso = True
                break
            i += 1
        r = self.engine.execute("SELECT nombre_heroes from heroes")
        rowfilter = ""
        i = 1
        for row in r:
            if i == its:
                rowfilter = row[0]
            i += 1
        if paso is False:
            return None
        return "Su personaje es " + rowfilter

    def Seleccion(self, exclusion_fila, exclusion_columna, incert, numbers):
        """Metodo que se encarga de
        seleccionar preguntas evitando exclusiones"""
        i = 0
        seleccion = [0, 0]
        a = random.randint(2, self.columnumber - 2)
        b = random.randint(1, self.rownumber)
        seleccion[0] = a
        seleccion[1] = b
        while exclusion_columna[a] is True or exclusion_fila[b] is True:
            i = i + 1
            if incert is False:
                a = random.randint(2, self.columnumber - 2)
                b = random.randint(1, self.rownumber)
                seleccion[0] = a
                seleccion[1] = b
            else:
                b = random.randint(1, self.rownumber)
                a = self.columnumber - 1
                seleccion[0] = a
                seleccion[1] = b
            if i > 3000:
                incert = True
            if i > 200000:
                seleccion = None
                break
        return seleccion
