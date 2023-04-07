from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL, Optional, ValidationError
from app.models.checks import Check
from flask_user import current_user

class CheckForm(FlaskForm):
    name = StringField('Check Name', validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired(), URL()])
    method = SelectField('Method', choices=["GET", "POST"])
    content = TextAreaField('Body Content', validators=[Optional()])
    enabled = BooleanField('Enabled', default=True)
    send = SubmitField("Submit")

    def validate_name(self, name):
        user_id = current_user.id
        check = Check.query.filter_by(user_id=user_id, name=name.data).first()
        if check is not None:
            raise ValidationError('You have already created a check with this name. Please choose a different name.')
