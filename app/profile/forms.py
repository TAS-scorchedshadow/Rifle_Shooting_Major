# -- Dylan Huynh --
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, PasswordField, SubmitField, BooleanField, HiddenField, \
    EmailField, DateField
from wtforms.validators import InputRequired, DataRequired, EqualTo, NumberRange


class updateInfoForm(FlaskForm):
    """
    Form for registering a user on the application
    """
    userID = HiddenField()
    fName = StringField("First Name", validators=[InputRequired()])
    sName = StringField("Last Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    gradYr = IntegerField("Graduation Year", validators=[InputRequired(), NumberRange(min=2000, max=9999)])
    mobile = StringField("Mobile", validators=[InputRequired()])
    rifle_serial = StringField("Rifle Serial", validators=[InputRequired()])
    schoolID = StringField("School ID", validators=[InputRequired()])
    shooterID = StringField("Shooter ID", validators=[InputRequired()])
    permitType = StringField("Permit Type", validators=[InputRequired()])
    permitNumber = StringField("Permit Number", validators=[InputRequired()])
    permitExpiry = DateField("Permit Expiry", validators=[InputRequired()])

    submit = SubmitField("Save")

