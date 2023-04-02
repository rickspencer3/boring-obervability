from app.extensions import db
from app.models.anomaly_detector_check import anomaly_detector_check_table
class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.Integer, primary_key = True)
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_check_table, back_populates='checks')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    content = db.Column(db.String(600))
    method = db.Column(db.String(10))
    user = db.relationship("User", back_populates = "checks")
    enabled = db.Column(db.Boolean, default=True)
