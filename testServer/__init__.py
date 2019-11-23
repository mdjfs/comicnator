# Hai Hai
from flask import Flask
from flask import render_template
from flask import request
from flask import session
from flask import flash
from flask import make_response

import form

app = Flask(__name__, template_folder="archivos_html")
app.secret_key = "my_secret_key"


@app.route("/", methods=["GET", "POST"])
def index():
    comment_form = form.CommentForm(request.form)
    custome_cookie = request.cookies.get("custom_cookie")
    print(custome_cookie)
    if request.method == "POST" and comment_form.validate():
        username = comment_form.username.data
        sucess_message = 'Bienvenido ' + username
        flash(sucess_message)
        session["username"] = username
    title = "Curso Flask"
    return render_template("index.html", title=title, form=comment_form)


@app.route("/cookie")
def cookie():
    response = make_response(render_template("cookie.html"))
    response.set_cookie("custom_cookie", "Marcos")
    return response


@app.route("/params/")
@app.route("/params/<name>/")
def params(name="default"):
    return render_template("user.html", name=name)
