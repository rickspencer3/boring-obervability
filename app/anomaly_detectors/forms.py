from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField, SubmitField
from wtforms.validators import DataRequired

class AnomalyDetectorForm(FlaskForm):
    name = StringField('Anomaly Detector Name', validators=[DataRequired()])
    send = SubmitField("Submit")

class LatencyDetectorForm(AnomalyDetectorForm):
    type = HiddenField(default="latency")
    latency_lower_bound = IntegerField('Latency Lower Bound', validators=[DataRequired()])

class ErrorDetectorForm(AnomalyDetectorForm):
    type = HiddenField(default="error")
    