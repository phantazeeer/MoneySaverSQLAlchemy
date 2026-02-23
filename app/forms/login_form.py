from wtforms import Form, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email


class LoginForm(Form):
    email = StringField("Введите свой email", validators=[DataRequired(), Email()])
    password = PasswordField("Введите свой пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
