from app.extensions import db, generate_id_string
from app.models.anomaly_detector_check import anomaly_detector_check_table
from cryptography.fernet import Fernet
from flask import current_app
from sqlalchemy.orm import validates

class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_check_table, back_populates='checks')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id')) 
    name = db.Column(db.String(100))
    user = db.relationship("User", back_populates = "checks")
    enabled = db.Column(db.Boolean, default=True)
    type = db.Column(db.String(20), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_user_id_name'),)

    __mapper_args__ = {
        'polymorphic_identity': 'check',
        'polymorphic_on': type
    }

    def run(self):
        raise NotImplementedError("Subclasses should implement this method")
    
    @property
    def form_class():
        return None

class InfluxDBCheck(Check):
    database = db.Column(db.String(100))
    host = db.Column(db.String(100))
    _token = db.Column("token", db.LargeBinary)
    org = db.Column(db.String(100))

    @property
    def token(self):
        f = Fernet(current_app.config['FERNET_KEY'])
        return f.decrypt(self._token).decode('utf-8')

    @token.setter
    def token(self, plaintext_value):
        f = Fernet(current_app.config['FERNET_KEY'])
        self._token = f.encrypt(plaintext_value.encode('utf-8'))
    
    __mapper_args__ = {
    'polymorphic_identity': 'influxdb',
    }


class InfluxDBWriteCheck(InfluxDBCheck):
    line_protocol = db.Column(db.String(300))
    api_version = db.Column(db.Integer)

    @validates('api_version')
    def validate_api_version(self, key, api_version):
        if api_version not in (1, 2):
            raise ValueError("api_version must be either 1 or 2")
        return api_version

    def run(self):
        print(f"run InfluxDBWriteCheck {self.id}, {self.name}")

    @property
    def form_class(self):
        import app.checks.forms as forms
        return forms.InfluxDBWriteForm

    __mapper_args__ = {
    'polymorphic_identity': 'influxdb_write',
    }

