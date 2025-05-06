from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegisterForm(FlaskForm):
    email = EmailField('Логин / Email', validators=[DataRequired(),
                                                    Email(message='Некорректный email')])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=6,
                                                          message='Пароль должен быть не менее 6 символов')])
    password_again = PasswordField('Повторите пароль',
                                   validators=[DataRequired(), EqualTo('password',
                                                                       message='Пароли должны совпадать')])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[Optional()])
    age = StringField('Возраст', validators=[Optional()])

    city_from = StringField('Родной город', validators=[Optional()])

    submit = SubmitField('Зарегистрироваться')
