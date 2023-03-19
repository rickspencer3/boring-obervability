from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class NotificationChannelForm(FlaskForm):
    name = StringField('Notication Channel Name', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired(), Email()])
    type = SelectField('Type', choices=["Email"], validators=[DataRequired()])
    send = SubmitField("Submit")