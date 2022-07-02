# -- Ryan Tan --
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectField, SubmitField, HiddenField


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
    weeks = SelectField(u'Uploading Shot Data From',
                        choices=[(1, 'Last Week'), (4, 'Last Month'), (12, 'Last 3 Months'), (56, 'Last Year')])
    total = HiddenField("Total")

