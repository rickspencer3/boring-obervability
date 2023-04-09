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

    def validate_name(self, field):
        # If the form has a check_id attribute, it means we're editing an existing check
        if hasattr(self, 'check_id'):
            original_check = Check.query.get(self.check_id)
            if original_check.name != field.data:
                existing_check = Check.query.filter_by(user_id=original_check.user_id, name=field.data).first()
                if existing_check:
                    raise ValidationError("You have already created a check with this name. Please choose a different name.")
        else:
            # This part handles the validation when creating a new check
            existing_check = Check.query.filter_by(user_id=current_user.id, name=field.data).first()
            if existing_check:
                raise ValidationError("You have already created a check with this name. Please choose a different name.")