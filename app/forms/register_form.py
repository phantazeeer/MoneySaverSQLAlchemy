from wtforms import Form, StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(Form):
    username = StringField("Введите имя пользователя", validators=[DataRequired()])
    email = EmailField("Введите свой email", validators=[DataRequired()])
    password = PasswordField("Введите свой пароль", validators=[DataRequired()])
    submit = SubmitField("Зарегистрироваться")
