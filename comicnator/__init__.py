from os import makedirs
from pathlib import Path
from random import randint

from flask import Flask
from flask_jsglue import JSGlue

from comicnator import database, routes
from comicnator.database import (
    GameSessions,
    HeroesMarvel,
    MarvelSugerencias,
    User,
    db)


def create_app():
    app = Comicnator(__name__)
    try:
        makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    app.config.from_pyfile("config.py")
    database_file = Path(app.instance_path, "database.sqlite").absolute()
    default_conf = {
        # "SERVER_NAME": "127.0.0.1:8080",
        "FLASK_ENV": "development",
        "SECRET_KEY": "secre-key-do-not-hack!!",
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_file}",
    }
    app.config.from_mapping(default_conf)
    app.register_blueprint(routes.bp)
    JSGlue(app)
    database.init_app(app)
    return app


class Comicnator(Flask):
    """ Clase que contiene todos los metodos de la Aplicacion """

    def __init__(self, *args, **kwargs):
        """ Metodo init que tiene las variables a usar en la
        Aplicacion """
        super().__init__(*args, **kwargs, instance_relative_config=True)
        self._rownumber = None
        self._columnumber = None
        self._rownumber_c = 0
        self._columnumber_c = 0

    @property
    def rownumber(self):
        self._rownumber_c += 1
        if self._rownumber_c > 100:
            self._rownumber_c = 0
            self._rownumber = None
        if self._rownumber is None:
            self._rownumber = db.session.query(HeroesMarvel).count()
        return self._rownumber

    @property
    def columnumber(self):
        self._columnumber_c += 1
        if self._columnumber_c > 100:
            self._columnumber_c = 0
            self._columnumber = None
        if self._columnumber is None:
            self._columnumber = len(HeroesMarvel.__table__.columns.keys())
        return self._columnumber

    def start_game(self):
        game_session = GameSessions()
        game_session.exclusion_fila = (False for i in range(self.rownumber))
        game_session.exclusion_columna = (False for i in
                                          range(self.columnumber))
        game_session.probable = (0.0 for i in range(self.rownumber))
        game_session.incert = False
        game_session.adivino = False
        game_session.posicion = self.seleccion(
            game_session.exclusion_fila,
            game_session.exclusion_columna,
            game_session.incert,
        )
        db.session.add(game_session)
        db.session.commit()
        return game_session.id

    def interaccion(self, session_id, form):
        """ El metodo mas grueso de lo grueso, es decir,
        xD, se encarga de manejar todo lo que son las preguntas
        y respuestas """
        game_session = GameSessions.query.filter_by(id=session_id).first()
        # verifico si no hay nuevos personajes
        if len(game_session.exclusion_fila) < self.rownumber:
            diferencia = self.rownumber - len(game_session.exclusion_fila)
            i = 0
            lista_exclusion = list(game_session.exclusion_fila)
            while i < diferencia:
                lista_exclusion.append(True)
                i += 1
                # no se toman en cuenta nuevos personajes en una sesion
            game_session.exclusion_fila = tuple(lista_exclusion)
        if len(game_session.probable) < self.rownumber:
            diferencia = self.rownumber - len(game_session.probable)
            lista_probable = list(game_session.probable)
            i = 0
            while i < diferencia:
                lista_probable.append(0)
                i += 1
                # no se toman en cuenta nuevos personajes en una sesion
            game_session.probable = tuple(lista_probable)
        if "si" in form:
            self.exclusion(game_session, True)
            self.probabilidad(game_session, True)
        elif "no" in form:
            self.exclusion(game_session, False)
            self.probabilidad(game_session, False)
        elif "no lo se" in form:
            pass
        finish = game_session.is_final
        if finish:
            game_session.incert = self.habilitar_incertidumbre(
                game_session.exclusion_columna, game_session.probable,
            )
            if game_session.incert:
                self.quitar_prob(game_session)
                finish = False
        game_session.posicion = self.seleccion(
            game_session.exclusion_fila,
            game_session.exclusion_columna,
            game_session.incert,
        )
        if finish:
            question = self.get_person(game_session.probable)
            if game_session.posicion is None or question is None:
                question = "No pudimos encontrar tu personaje"
            game_session.adivino = True
        else:
            if game_session.posicion:
                question = self.question(game_session.posicion)
            else:
                question = "No pudimos encontrar tu personaje"
                game_session.adivino = True
        db.session.add(game_session)
        db.session.commit()
        return question, game_session.adivino

    def question(self, pos):
        """Metodo que se encarga de buscar en la base de datos
        la posicion en que se encuentra el usuario"""
        filtro = HeroesMarvel.__table__.columns.keys()
        columna = filtro[pos[0]]
        verbos = HeroesMarvel.query.all()
        verb = None
        keys = None
        for i, verbo in enumerate(verbos):
            if i == pos[1]:
                verb = verbo.__dict__
                keys = verb.keys()
        columnsattrs = []
        for name in filtro:
            for key in keys:
                if key in name:
                    asigna = True
                    for element in columnsattrs:
                        if element == key:
                            asigna = False
                    if asigna:
                        columnsattrs.append(key)
        fila = verb[columnsattrs[pos[0]]]
        return "Su personaje " + columna + " " + fila

    def exclusion(self, game_session, mode):
        """Metodo que se encarga de excluir personajes
        para que no salgan preguntas que no tengan que ver"""
        filtro = HeroesMarvel.__table__.columns.keys()
        verbos = HeroesMarvel.query.all()
        pos = game_session.posicion
        verb = None
        valores = []
        for verbo in verbos:
            verb = verbo.__dict__
            keys = verb.keys()
            for key in keys:
                if key in filtro[pos[0]]:
                    if key != "id":
                        valores.append(verb[key])
        exclusion_fila = list(game_session.exclusion_fila)
        exclusion_columna = list(game_session.exclusion_columna)
        if mode is True:
            exclusion_columna[pos[0]] = True
            for i, row in enumerate(valores):
                if i == pos[1]:
                    rowfilter = row
            for i, row in enumerate(valores):
                if row != rowfilter:
                    exclusion_fila[i] = True
        else:
            rowfilter = ""
            for i, row in enumerate(valores):
                if i == pos[1]:
                    rowfilter = row
            for i, row in enumerate(valores):
                if row == rowfilter:
                    exclusion_fila[i] = True
        game_session.exclusion_fila = exclusion_fila
        game_session.exclusion_columna = exclusion_columna

    def habilitar_incertidumbre(self, exclusion_columna, prob):
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

    def quitar_prob(self, game_session):
        """Este metodo si encuentra una probabilidad mayor de 100, la baja
        hasta que quede en menos de 100"""
        prob = list(game_session.probable)
        j = 5
        while j > 1:
            j = 0
            for i in range(len(prob)):
                if prob[i] > 100:
                    prob[i] -= 20
                    j += 1
        game_session.probable = prob

    def probabilidad(self, game_session, mode):
        """Este metodo da probabilidades a unos personajes
        u otros dependiendo la respuesta"""
        filtro = HeroesMarvel.__table__.columns.keys()
        verbos = HeroesMarvel.query.all()
        pos = game_session.posicion
        respuestas = []
        for verbo in verbos:
            for key, value in verbo.__dict__.items():
                if key != "id" and key in filtro[pos[0]]:
                    respuestas.append(value)
        probabilidad = list(game_session.probable)
        repitio = [False for i in range(len(probabilidad))]
        rowfilter = respuestas[pos[1]]
        repetido = 0
        for i, row in enumerate(respuestas):
            if row == rowfilter:
                repitio[i] = True
                repetido += 1
        filas = self.rownumber
        prob = repetido / filas * 100
        if mode is True:
            for x in range(filas):
                if repitio[x]:
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
                if not repitio[x]:
                    if prob > 50:
                        probabilidad[x] += 80
                    if prob > 20 and prob < 50:
                        probabilidad[x] += 40
                    if prob < 20:
                        probabilidad[x] += 10
        game_session.probable = probabilidad

    def get_person(self, probability):
        """Obtiene el nombre del personaje"""
        pos = None
        for i, prob in enumerate(probability):
            if prob > 100:
                pos = i
                break
        else:
            return None
        for i, heroe in enumerate(HeroesMarvel.query):
            if i == pos:
                return "Su personaje es " + heroe.nombre

    def seleccion(self, exclusion_fila, exclusion_columna, incert):
        """Metodo que se encarga de
        seleccionar preguntas evitando exclusiones"""
        i = 0
        cols = self.columnumber - 1
        rows = self.rownumber - 1
        initcols = 2
        # debe saltarse id y nombre
        limitcols = cols - 1
        # no puede tomar la incertidumbre
        verificar_seleccion_col = initcols
        excepcion_seleccion_col = True
        excepcion_seleccion_row = True
        seleccion = None
        while verificar_seleccion_col <= cols:
            verificar_seleccion_row = 0
            while verificar_seleccion_row < rows:
                seleccion = [verificar_seleccion_col,
                             verificar_seleccion_row]
                if exclusion_columna[seleccion[0]] is False:
                    excepcion_seleccion_col = False
                if exclusion_fila[seleccion[1]] is False:
                    excepcion_seleccion_row = False
                verificar_seleccion_row += 1
            verificar_seleccion_col += 1
        if excepcion_seleccion_col or excepcion_seleccion_row:
            seleccion = None
        else:
            seleccion = [randint(initcols, limitcols), randint(0, rows)]
            while (exclusion_columna[seleccion[0]] or
                   exclusion_fila[seleccion[1]]):
                i = i + 1
                if incert is False:
                    seleccion = [randint(initcols, limitcols),
                                 randint(0, rows)]
                else:
                    seleccion = [cols, randint(0, rows)]
                    # toma la incertidumbre
                if i > 3000:
                    incert = True
                    # activa la incertidumbre a los 3000 intentos
        return seleccion

    def verificacion(self, username, password):
        success_message = None
        user = User.query.filter_by(username=username).first()
        if user is not None and user.verify(password):
            success_message = "Bienvenido " + username
        return success_message

    def insertar_sugerencia(self, data):
        Sugerencia = MarvelSugerencias(
            nombre=data[1],
            genero=data[2],
            origen=data[3],
            empezo=data[4],
            capacidad=data[5],
            describe=data[6],
        )
        db.session.add(Sugerencia)
        db.session.commit()

    def insertar(self, data):
        Heroe = HeroesMarvel(
            id=self.rownumber + 1,
            nombre=data[1],
            genero=data[2],
            origen=data[3],
            empezo=data[4],
            capacidad=data[5],
            describe=data[6],
        )
        db.session.add(Heroe)
        db.session.commit()
        self._rownumber_c += 100

    def borrar_sugerencia(self):
        sug = db.session.query(MarvelSugerencias).first()
        db.session.delete(sug)
        db.session.commit()

    def solicitar_sugerencia(self):
        sug = db.session.query(MarvelSugerencias).first()
        if sug is not None:
            return [
                sug.id,
                sug.nombre,
                sug.genero,
                sug.origen,
                sug.empezo,
                sug.capacidad,
                sug.describe,
            ]
        else:
            return None

    def return_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        return user
