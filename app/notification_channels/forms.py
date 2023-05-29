from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, URL

class NotificationChannelForm(FlaskForm):
    name = StringField('Channel Name', validators=[DataRequired()])
    send = SubmitField("Submit")
    enabled = BooleanField('Enabled', default=True) 

    class Meta:
        abstract = True

class EmailChannelForm(NotificationChannelForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])

class WebhookForm(NotADirectoryError):
    url = StringField('URl', validators=[DataRequired(), URL()])
