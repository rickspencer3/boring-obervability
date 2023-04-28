from app.extensions import db, generate_id_string
from app.models.anomaly_detector_check import anomaly_detector_check_table
from cryptography.fernet import Fernet
from flask import current_app

class Check(db.Model):
    __tablename__ = 'checks'
    id = db.Column(db.String(8), primary_key=True, default=generate_id_string)
    anomaly_detectors = db.relationship('AnomalyDetector', secondary=anomaly_detector_check_table, back_populates='checks')
    user_id = db.Column(db.String(36), db.ForeignKey('users.id')) 
    name = db.Column(db.String(100))
    user = db.relationship("User", back_populates = "checks")
    enabled = db.Column(db.Boolean, default=True)
    type = db.Column(db.String(10), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='uq_user_id_name'),)

    __mapper_args__ = {
        'polymorphic_identity': 'check',
        'polymorphic_on': type
    }

    def run(self):
        raise NotImplementedError("Subclasses should implement this method")

class HTTPCheck(Check):
    url = db.Column(db.String(100))
    content = db.Column(db.String(600))
    method = db.Column(db.String(10))

    __mapper_args__ = {
    'polymorphic_identity': 'http',
    }

    def run(self):
        print(f"run HTTPCheck {self.id}, {self.name}")

class InfluxDBCheck(Check):
    database = db.Column(db.String(100))
    _token = db.Column("value", db.LargeBinary)

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
        
class InfluxDBReadCheck(InfluxDBCheck):
    sql = db.Column(db.String(300))

    def run(self):
        print(f"run InfluxDBReadCheck {self.id}, {self.name}")

    __mapper_args__ = {
    'polymorphic_identity': 'influxdb_read',
    }

class InfluxDBWriteCheck(InfluxDBCheck):
    line_protocol = db.Column(db.String(300))

    def run(self):
        print(f"run InfluxDBWriteCheck {self.id}, {self.name}")

    __mapper_args__ = {
    'polymorphic_identity': 'influxdb_write',
    }