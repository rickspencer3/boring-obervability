import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'BeTjncDRQSvNbH0LLXHTMJg9gds16n9z'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp-relay.sendinblue.com'
    MAIL_PORT = 587
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'richard.linger.spencer.3@gmail.com'
    MAIL_PASSWORD = 'I8BzV0v4FWgjX5Rh'
    MAIL_DEFAULT_SENDER = '"Boring Observability" <noreply@boring-observability.com>'

    # Flask-User settings
    USER_APP_NAME = "Boring Observability"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form

    # InfluxDB settings
    INFLUXDB_BUCKET = "boring-observability"
    INFLUXDB_WRITE_TOKEN = "dVonwGMYxmNT3_KIiZ5zBFIHllWlLWz5xLbuE2kvgzmuqWo8_JyyFDXZDqRaJtP9L2gnyY33GenWoKRBNJKWQg=="
    INFLUXDB_READ_TOKEN = "dVonwGMYxmNT3_KIiZ5zBFIHllWlLWz5xLbuE2kvgzmuqWo8_JyyFDXZDqRaJtP9L2gnyY33GenWoKRBNJKWQg=="
    INFLUXDB_HOST = "https://us-east-1-1.aws.cloud2.influxdata.com/"
    INFLUXDB_FLIGHT_HOST = "us-east-1-1.aws.cloud2.influxdata.com"
    INFLUXDB_ORG_ID = "847e9dbb25976492"
    FERNET_KEY = "VxKtq48iHIg1-u3iiNeUuqY5eB-jqDlMVq0BMlmffjY="
    