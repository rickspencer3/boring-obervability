from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL, Optional


class CheckForm(FlaskForm):
    name = StringField('Check Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    method = SelectField('Method', choices=["GET","POST"])
    content = TextAreaField('Body Content', validators=[Optional()])
    enabled = BooleanField('Enabled', default=True) 
    send = SubmitField("Submit")

    