# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, Length, EqualTo, ValidationError
import re

# Función para validar la fortaleza de la contraseña
def password_check(form, field):
    password = field.data
    if len(password) < 8:
        raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
    if not re.search("[a-z]", password):
        raise ValidationError('La contraseña debe contener al menos una letra minúscula.')
    if not re.search("[A-Z]", password):
        raise ValidationError('La contraseña debe contener al menos una letra mayúscula.')
    if not re.search("[0-9]", password):
        raise ValidationError('La contraseña debe contener al menos un número.')
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError('La contraseña debe contener al menos un carácter especial.')

def validate_email(form, field):
    email = field.data
    if not email.contains('@unl.edu.ec'):
        raise ValidationError('Por favor, introduce un correo electrónico.')


# login and registration

class LoginForm(FlaskForm):
    email = StringField('Email',
                        id='email_login',
                        validators=[DataRequired(message='El correo electrónico es obligatorio.'), 
                                    Email(message='Por favor, introduce un correo electrónico válido.')])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired(message='La contraseña es obligatoria.')])
    remember = BooleanField('Remember me', id='remember')

class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired(message='El nombre de usuario es obligatorio.'),
                                     Length(min=3, max=20, message='El nombre de usuario debe tener entre 3 y 20 caracteres.')])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(message='El correo electrónico es obligatorio.'), 
                                  Email(message='Por favor, introduce un correo electrónico válido.'),
                                  validate_email])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired(message='La contraseña es obligatoria.'),
                                         password_check])
    confirm_password = PasswordField('Confirm Password',
                                     id='pwd_confirm',
                                     validators=[DataRequired(message='La confirmación de la contraseña es obligatoria.'),
                                                 EqualTo('password', message='Las contraseñas deben coincidir.')])

    def validate_username(self, username):
        if not username.data.isalnum():
            raise ValidationError('El nombre de usuario solo puede contener letras y números.')

    
