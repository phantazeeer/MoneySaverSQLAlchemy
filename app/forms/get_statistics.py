from wtforms import DateField, Form, SubmitField
from wtforms.validators import DataRequired


class ChooseDateForm(Form):
    start = DateField("С", format='%Y-%m-%d', validators=[DataRequired()])
    end = DateField("До", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Показать")
