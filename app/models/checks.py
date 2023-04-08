from app.extensions import db
from app.models.anomaly_detector_check import anomaly_detector_check_table
from app.extensions import generate_id_string

class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_check_table, back_populates='checks')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id')) 
    name = db.Column(db.String(100))
    url = db.Column(db.String(100))
    content = db.Column(db.String(600))
    method = db.Column(db.String(10))
    user = db.relationship("User", back_populates = "checks")
    enabled = db.Column(db.Boolean, default=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_user_id_name'),)
