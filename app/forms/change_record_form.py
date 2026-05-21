from wtforms import Form, IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class ChangeRecordForm(Form):
    value = IntegerField("Введите значение", validators=[DataRequired()])
    operation_type = SelectField(
        "Введите тип записи",
        choices=[("0", "доход"), ("1", "расход")],
        validators=[DataRequired()],)
    comment = TextAreaField("Введите свой комментарий")
    category = SelectField("Выберите категорию")
    submit = SubmitField("Изменить запись")

    def __init__(self, categories: list):
        super().__init__()
        self.category.choices = [("", "Не выбрана")] + [(i, i) for i in categories]
