from wtforms import Form, PasswordField, StringField, validators


class learnForm(Form):
    username = StringField(
        "admin", [validators.Required(message="Este campo es obligatorio")]
    )
    password = PasswordField(
        "password", [validators.Required(message="Este campo es obligatorio")]
    )
