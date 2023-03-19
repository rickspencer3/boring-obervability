from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class HeaderForm(FlaskForm):
    name = StringField('Header Name', validators=[DataRequired()])
    key = StringField('Key', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    send = SubmitField("Submit")
