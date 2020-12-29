from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField, \
    RadioField, BooleanField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, InputRequired, EqualTo


# This file contains all the required forms from various parts of this project

# Form for uploading files
# -- Ryan Tan --
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
    rifleRange = SelectField("Rifle Range:", choices=[('Malabar', 'Malabar')])
    distance = SelectField("Distance:", choices=[('300m', '300m'), ('500m', '500m'), ('600m', '600m'),
                                                 ('700m', '700m'), ('800m', '800m')])
    weather = SelectField("Weather:", choices=[('Sunny', 'Sunny'), ('Cloudy', 'Cloudy'), ('Windy', 'Windy'),
                                               ('Rain', 'Rain'), ('Storm', 'Storm')])
    submit = SubmitField("Submit")
    identifier = HiddenField("Upload/Verify", default="upload")
    submit = SubmitField("Submit")
    shootInfo = HiddenField("Data")
    success = HiddenField("Success")
    total = HiddenField("Total")


# Form for registering
# -- Dylan Huynh --
class signUpForm(FlaskForm):
    fName = StringField("Enter First Name:",validators=[InputRequired()])
    sName = StringField("Enter Last Name:",validators=[InputRequired()])
    school = SelectField("Select a school", choices=[('SBHS','SBHS')])
    schoolID = StringField("School ID:",validators=[InputRequired()])
    shooterID = StringField("School ID:", validators=[InputRequired()])
    password = PasswordField("Password:")
    confirmPassword = PasswordField("Password:")

    submit = SubmitField("Sign Up")


# Form for logging in
# -- Dylan Huynh --
class signInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    submit = SubmitField('Request password reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

# Form for report page
# -- Henry Guo --
class reportForm(FlaskForm):
    date = SelectField('Date',)
    submit = SubmitField("Select")

# -- Rishi Wig --
class shooterSelect(FlaskForm):
    team = SelectField("Team")
    name = SelectField("Name")

# # Forms for comparisons
# # -- Rishi Wig --
# class comparativeSelect(FlaskForm):
#     graphType = RadioField('Graph', choices=['Line', 'Bar'])
#     shooter_username_one = SelectField('Username', choices=get_all_usernames())
#     shooter_username_two = SelectField('Username', choices=get_all_usernames())
#
#     shooting_range_one = SelectField('Range')
#     shooting_range_two = SelectField('Range')
#
#     dates_one = SelectField('Dates')
#     dates_two = SelectField('Dates')
#
#     submit = SubmitField('ENTER')
#
#
# class comparativeSpecify(FlaskForm):
#     shooter_username_one = SelectField('Username', choices=get_all_shooter_names())