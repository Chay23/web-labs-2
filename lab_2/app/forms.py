from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


# Regexp
#  Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
#                                               'Username must have only '
#                                               'letters, numbers, dots or '
#                                               'underscores')])
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=25,
                                                          message="Username length should be between 4 and 25"),
                                                   DataRequired(message="This field can't be empty")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6, message="Length of password should be greater than 6")])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sing up')