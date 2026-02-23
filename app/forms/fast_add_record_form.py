from wtforms import Form, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class FastAddRecordForm(Form):
    value = IntegerField("Введите значение", validators=[DataRequired()])
    operation_type = SelectField("Введите тип записи", choices=[(0, "доход"), (1, "расход")], validators=[DataRequired()], default=0)
    submit = SubmitField("Добавить запись")
