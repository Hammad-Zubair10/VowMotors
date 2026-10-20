from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField, PasswordField, DecimalField, IntegerField,
    SelectField, TextAreaField, MultipleFileField, SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send reset link')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm new password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')],
    )
    submit = SubmitField('Reset password')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField(
        'Confirm new password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')],
    )
    submit = SubmitField('Update password')


class VehicleForm(FlaskForm):
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1950, max=2100)])
    make = StringField('Make', validators=[DataRequired(), Length(max=60)])
    model = StringField('Model', validators=[DataRequired(), Length(max=60)])
    trim = StringField('Trim', validators=[Optional(), Length(max=60)])
    body_style = SelectField(
        'Body style',
        choices=[('Car', 'Car'), ('SUV', 'SUV'), ('Truck', 'Truck'), ('Commercial', 'Commercial')],
        validators=[DataRequired()],
    )
    price = DecimalField('Price ($)', validators=[DataRequired(), NumberRange(min=0)])
    mileage = IntegerField('Mileage (km)', validators=[Optional(), NumberRange(min=0)])
    exterior_color = StringField('Exterior color', validators=[Optional(), Length(max=40)])
    transmission = SelectField(
        'Transmission',
        choices=[('', 'Select one'), ('Automatic', 'Automatic'), ('Manual', 'Manual'), ('CVT', 'CVT')],
        validators=[Optional()],
    )
    fuel_type = SelectField(
        'Fuel type',
        choices=[
            ('', 'Select one'), ('Gasoline', 'Gasoline'), ('Diesel', 'Diesel'),
            ('Hybrid', 'Hybrid'), ('Electric', 'Electric'),
        ],
        validators=[Optional()],
    )
    vin = StringField('VIN', validators=[Optional(), Length(max=32)])
    status = SelectField(
        'Status', choices=[('available', 'Available'), ('sold', 'Sold')], validators=[DataRequired()]
    )
    description = TextAreaField('Description', validators=[Optional(), Length(max=4000)])
    photos = MultipleFileField(
        'Photos', validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg', 'webp'], 'Images only')]
    )
    submit = SubmitField('Save vehicle')
