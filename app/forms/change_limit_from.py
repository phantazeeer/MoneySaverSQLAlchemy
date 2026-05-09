from wtforms import Form, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ChangeLimitForm(Form):
    value = IntegerField("Значение лимита:", validators=[DataRequired(), NumberRange(min=0)])
    period = SelectField("За какой период:", choices=[("day", "1 день"), ("month", "1 месяц"), ("year", "1 год")])
    submit = SubmitField("Добавить цель")
