from wtforms import Form, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired


class FastAddRecordForm(Form):
    value = IntegerField("Введите значение", validators=[DataRequired()])
    operation_type = SelectField(
        "Введите тип записи",
        choices=[(0, "доход"), (1, "расход")],
        validators=[DataRequired()],
        default=0,
    )
    comment = StringField("Введите комментарий к записи")
    category = SelectField("Выберите категорию")
    submit = SubmitField("Добавить запись")

    def __init__(self, categories: list):
        super().__init__()
        self.category.choices = [(i, i) for i in categories]
