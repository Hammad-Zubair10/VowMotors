from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class ContactForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=180)])
    phone = StringField('Phone', validators=[Optional(), Length(max=30)])
    subject = StringField('Subject', validators=[Optional(), Length(max=150)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=4000)])


class FinancingForm(FlaskForm):
    full_name = StringField('Full name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=180)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=30)])
    employment_status = SelectField(
        'Employment status',
        choices=[
            ('', 'Select one'),
            ('Employed', 'Employed'),
            ('Self-employed', 'Self-employed'),
            ('Retired', 'Retired'),
            ('Other', 'Other'),
        ],
        validators=[Optional()],
    )
    annual_income = StringField('Approximate annual income', validators=[Optional(), Length(max=40)])
    down_payment = StringField('Planned down payment', validators=[Optional(), Length(max=40)])
    vehicle_interest = StringField('Vehicle you are interested in', validators=[Optional(), Length(max=120)])
    notes = TextAreaField('Anything else we should know?', validators=[Optional(), Length(max=2000)])
