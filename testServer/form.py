from wtforms import Form, StringField, TextField
from wtforms.fields.html5 import EmailField

from wtforms import validators


class CommentForm(Form):
    username = StringField(
        "username",
        [
            validators.length(min=4, max=25, message="Username valido!"),
            validators.Required(message=" El username es requerido !"),
        ],
    )
    email = EmailField("Correo electronico")
    comment = TextField("Comentario")
