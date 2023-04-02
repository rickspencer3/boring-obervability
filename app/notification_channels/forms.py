from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class NotificationChannelForm(FlaskForm):
    name = StringField('Channel Name', validators=[DataRequired()])
    send = SubmitField("Submit")

    class Meta:
        abstract = True

class EmailChannelForm(NotificationChannelForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
