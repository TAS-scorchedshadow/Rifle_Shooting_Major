# -- Dylan Huynh --
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField, BooleanField, EmailField
from wtforms.validators import InputRequired, DataRequired, EqualTo, NumberRange


class signUpForm(FlaskForm):
    """
    Form for registering a user on the application
    """
    fName = StringField("Enter First Name:", validators=[InputRequired()])
    sName = StringField("Enter Last Name:", validators=[InputRequired()])
    gradYr = IntegerField("Graduation Year:", validators=[InputRequired(), NumberRange(min=2000, max=9999)])
    schoolID = StringField("School ID:", validators=[InputRequired()])
    shooterID = StringField("Shooter ID:", validators=[InputRequired()])
    email = EmailField("Email:", validators=[InputRequired()])
    password = PasswordField("Password:", validators=[InputRequired()])
    confirmPassword = PasswordField("Password:", validators=[InputRequired()])

    submit = SubmitField("Sign Up")


class independentSignUpForm(FlaskForm):
    fName = StringField("Enter First Name:", validators=[InputRequired()])
    sName = StringField("Enter Last Name:", validators=[InputRequired()])
    shooterID = StringField("Shooter ID:", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password:")
    confirmPassword = PasswordField("Password:")

    submit = SubmitField("Sign Up")


class CoachSignUpForm(FlaskForm):
    fName = StringField("Enter First Name:", validators=[InputRequired()])
    sName = StringField("Enter Last Name:", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
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
    email = EmailField('Email', validators=[DataRequired()])
    submit = SubmitField('Request password reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

