from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional


class JobForm(FlaskForm):
    job = StringField('Название работы/задания', validators=[DataRequired()])
    work_size = IntegerField('Объем работы (в часах)',
                             validators=[DataRequired(),
                                         NumberRange(min=1,
                                                     message='Объем работы должен быть не менее 1 часа')])
    collaborators = StringField('ID участников (через запятую)', validators=[Optional()])
    category_ids = StringField('ID Категорий (через запятую)', validators=[Optional()])
    is_finished = BooleanField('Работа завершена?')
    submit = SubmitField('Сохранить работу')
