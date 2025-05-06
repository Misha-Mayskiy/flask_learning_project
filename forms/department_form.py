from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Optional


class DepartmentForm(FlaskForm):
    title = StringField('Название департамента', validators=[DataRequired()])
    chief = IntegerField('ID руководителя (Chief)', validators=[DataRequired()])
    members = StringField('ID участников (через запятую)', validators=[Optional()])
    email = EmailField('Email департамента', validators=[DataRequired(), Email(message='Некорректный email')])
    submit = SubmitField('Сохранить департамент')
