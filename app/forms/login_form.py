from wtforms import Form, StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired


class LoginForm(Form):
    email = EmailField("Введите свой email", validators=[DataRequired()])
    password = PasswordField("Введите свой пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
