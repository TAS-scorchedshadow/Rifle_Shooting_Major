from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField, \
    RadioField, BooleanField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, NumberRange


# This file contains all the required forms from various parts of this project

# -- Ryan Tan --
class uploadForm(FlaskForm):
    """
    Form fields to upload information on the shoot to be added to the database
    """
    file = MultipleFileField(u'Submit File')
    location = SelectField("Location:", choices=[('Malabar', 'Malabar')])
    # distance = SelectField("Distance:", choices=[('300m', "300"), ('500m', "500"), ('600m', "600"),
    #                                              ('700m', "700"), ('800m', "800")])
    weather = SelectField("Weather:", choices=[('Sunny', 'Sunny'), ('Cloudy', 'Cloudy'), ('Windy', 'Windy'),
                                               ('Rain', 'Rain'), ('Storm', 'Storm')])
    ammoType = SelectField("Ammo Type:", choices=[('ADI', 'ADI'), ('Winchester', 'Winchester'), ('PPU', 'PPU')])
    submit = SubmitField("Submit")
    identifier = HiddenField("Upload/Verify", default="upload")
    stageDump = HiddenField("Data")
    success = HiddenField("Success")
    weeks = SelectField(u'Uploading Shot Data From', choices=[(1, 'Last Week'), (4, 'Last Month'), (12, 'Last 3 Months'), (56, 'Last Year')])
    total = HiddenField("Total")


# -- Dylan Huynh --
class signUpForm(FlaskForm):
    """
    Form for registering a user on the application
    """
    fName = StringField("Enter First Name:",validators=[InputRequired()])
    sName = StringField("Enter Last Name:",validators=[InputRequired()])
    school = SelectField("Select a school", choices=[('SBHS','SBHS')])
    gradYr = IntegerField("Graduation Year:", validators=[InputRequired(), NumberRange(min=2000,max=9999)])
    schoolID = StringField("School ID:",validators=[InputRequired()])
    shooterID = StringField("Shooter ID:", validators=[InputRequired()])
    password = PasswordField("Password:")
    confirmPassword = PasswordField("Password:")

    submit = SubmitField("Sign Up")

class independentSignUpForm(FlaskForm):
    fName = StringField("Enter First Name:",validators=[InputRequired()])
    sName = StringField("Enter Last Name:",validators=[InputRequired()])
    shooterID = StringField("School ID:", validators=[InputRequired()])
    email = EmailField("Email",validators=[InputRequired()])
    password = PasswordField("Password:")
    confirmPassword = PasswordField("Password:")

    submit = SubmitField("Sign Up")

# -- Dylan Huynh --
class signInForm(FlaskForm):
    """
    Form for logging into the application
    """
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

# -- Henry Guo --
class reportForm(FlaskForm):
    """
    Forms for the report page
    """
    date = SelectField('Date',)
    submit = SubmitField("Select")

# -- Rishi Wig --
class profileSelect(FlaskForm):
    """
    Forms to select and change cells in info table on the profile page
    """
    cell = SelectField('Change cell', choices=[('sid','SID'),('dob', 'DOB'), ('rifleSerial', 'Rifle Serial'), ('schoolID', 'Student ID'),
                                               ("schoolYr", "Grade"), ("email", "Email"), ("permitNumber", "Permit"),
                                               ("permitExpiry", "Expiry"), ("sharing", "Sharing"),
                                               ("mobile", "Mobile"), ("class", "Class"), ("Mobile2", "Mobile")])
    data = StringField('Enter new data:')
    submit = SubmitField('ENTER')

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