from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, PasswordField, ValidationError
from wtforms.fields.html5 import EmailField, TelField
from wtforms.validators import Email, DataRequired, EqualTo, Length


class RegistrationForm(FlaskForm):
	name = StringField('Ваше имя: ', validators=[DataRequired(), Length(min=2, max=50, message='Имя должно быть от 2 до 50 символов')])
	email = EmailField('Почта: ', validators=[DataRequired()])
	password = PasswordField('Пароль: ', validators=[DataRequired(), Length(min=4, max=50, message='Пароль должен быть от 4 до 50 символов')])
	password2 = PasswordField('Повторите пароль: ', validators=[DataRequired(), EqualTo('password', message='Пароли не совпадают')])
	submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
	email = EmailField('Почта: ', validators=[DataRequired()])
	password = PasswordField('Пароль: ', validators=[DataRequired()])
	remember = BooleanField('Запомнить меня', default=False)
	submit = SubmitField('Войти')


class MakeOrderForm(FlaskForm):
	name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50)])
	surname = StringField('Фамилия', validators=[DataRequired()])
	phone_num = TelField('Телефон', validators=[DataRequired(), Length(min=4, max=50)])
	city = StringField('Город', validators=[DataRequired()])
	adress = StringField('Адрес', validators=[DataRequired()])
	submit = SubmitField('Перейти к оплате')