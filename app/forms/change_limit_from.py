from wtforms import Form, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class ChangeLimitForm(Form):
    value = IntegerField("Значение лимита:", validators=[DataRequired()])
    period = SelectField("За какой период:", choices=[("day", "1 день"), ("month", "1 месяц"), ("year", "1 год")])
    submit = SubmitField("Добавить цель")
