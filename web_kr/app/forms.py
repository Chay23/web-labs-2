from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, InputRequired
from wtforms.fields.html5 import DateField

from app.models import Car


class NewCarForm(FlaskForm):
    license_plate = StringField('License plate', validators=[Length(min=8, max=8,
                                                                    message="License plate length should be 8"),
                                                             DataRequired()])
    # Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    #        'Wrong license plate')])
    brand = StringField('Brand', validators=[DataRequired()])
    condition = SelectField('Condition', coerce=int, validators=[InputRequired()])
    on_go = SelectField('On go', choices=[('Yes', 'Yes'), ('No', 'No')])
    price = StringField('Price', validators=[DataRequired()])
    prod_date = DateField('DatePicker', format='%Y-%m-%d')
    submit = SubmitField('Create')

    def validate_licence_plate(self, field):
        if Car.query.filter_by(license_plate=field.data).first():
            raise ValidationError('Car already registered')


class EditCarForm(FlaskForm):
    license_plate = StringField('License plate', validators=[Length(min=8, max=8,
                                                                    message="License plate length should be 8"),
                                                             DataRequired()])
    # Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    #        'Wrong license plate')])
    brand = StringField('Brand', validators=[DataRequired()])
    condition = SelectField('Condition', coerce=int, validators=[InputRequired()])
    on_go = SelectField('On go', choices=[('Yes', 'Yes'), ('No', 'No')])
    price = StringField('Price', validators=[DataRequired()])
    prod_date = DateField('DatePicker', format='%Y-%m-%d')
    submit = SubmitField('Edit')

    def validate_licence_plate(self, field):
        if Car.query.filter_by(license_plate=field.data).first():
            raise ValidationError('Car already registered')