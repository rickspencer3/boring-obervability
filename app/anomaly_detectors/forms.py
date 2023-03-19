from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class AnomalyDetectorForm(FlaskForm):
    name = StringField('Anomaly Detector Name', validators=[DataRequired()])
    value = StringField('Value', validators=[DataRequired()])
    type = SelectField('Type', choices=["Error","Latency"], validators=[DataRequired()])
    send = SubmitField("Submit")