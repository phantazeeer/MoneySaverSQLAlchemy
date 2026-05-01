from wtforms import Form, IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class ChangeRecordForm(Form):
    value = IntegerField("Введите значение", validators=[DataRequired()])
    operation_type = SelectField("Введите тип записи", choices=[(0, "доход"), (1, "расход")], validators=[DataRequired()], default=0)
    comment = TextAreaField("Введите свой комментарий")
    category = SelectField("Выберите категорию")
    submit = SubmitField("Изменить запись")

    def __init__(self, categories: list):
        super().__init__()
        self.category.choices = [(i, i) for i in categories]
