from app.extensions import db

anomaly_detector_check_table = db.Table(
    'anomaly_detector_check',
    db.Column('anomaly_detector_id', db.Integer, db.ForeignKey('anomaly_detectors.id')),
    db.Column('check_id', db.Integer, db.ForeignKey('checks.id'))
)