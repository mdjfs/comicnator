from wtforms import Form, StringField, PasswordField, validators


class learnForm(Form):
    username = StringField(
        "admin", [validators.Required(message="Este campo es obligatorio")]
    )
    password = PasswordField(
        "password", [validators.Required(message="Este campo es obligatorio")]
    )
