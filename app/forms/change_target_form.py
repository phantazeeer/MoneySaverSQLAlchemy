from wtforms import Form, StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class ChangeTargetForm(Form):
    goal_name = StringField("Имя цели:", validators=[DataRequired()])
    goal_value = IntegerField("Значение цели:", validators=[DataRequired()])
    submit = SubmitField("Добавить цель")