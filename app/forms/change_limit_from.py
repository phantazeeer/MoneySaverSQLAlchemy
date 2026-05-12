from wtforms import DateField, Form, IntegerField, SelectField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, ValidationError


def at_least_one(form, field):
    if not field:
        raise ValidationError("Выберите хотя бы одну категорию")


class CreateLimitForm(Form):
    name = StringField("Название лимита", validators=[DataRequired()])
    value = IntegerField("Максимальная сумма", validators=[DataRequired(), NumberRange(min=1)])
    period = SelectField(
        "Период",
        choices=[
            ("month", "Ежемесячно"),
            ("week", "Еженедельно"),
            ("day", "Ежедневно"),
            ("once", "Одноразовый"),
        ],
        validators=[DataRequired()],
    )
    start = DateField("Начало", validators=[Optional()])
    end = DateField("Конец", validators=[Optional()])
    categories = SelectMultipleField("Категории", validators=[at_least_one])
    submit = SubmitField("Добавить лимит")
