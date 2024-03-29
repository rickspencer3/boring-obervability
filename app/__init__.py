from flask import Flask
from flask_user.user_manager import UserManager
from config import Config
from app.extensions import db, mail, influxdb_write

from app.models.users import User
from app.check_job import run_checks
from apscheduler.schedulers.background import BackgroundScheduler
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    db.app = app
    mail.init_app(app)
    app.influxdb_write = influxdb_write
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    with app.app_context():
        db.create_all()
        user_manager = UserManager(app, db, User)      
        
    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.checks import bp as checks_bp
    app.register_blueprint(checks_bp, url_prefix='/checks')

    from app.anomaly_detectors import bp as anomaly_detectors_bp
    app.register_blueprint(anomaly_detectors_bp, url_prefix='/anomaly_detectors')
    
    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    from app.headers import bp as headers_bp
    app.register_blueprint(headers_bp, url_prefix='/headers')

    from app.notification_channels import bp as channel_bp
    app.register_blueprint(channel_bp, url_prefix='/channels')

    # schedule the checks
    scheduler = BackgroundScheduler()

    # go ahead and run the checks one, then schedule
    run_checks()
    with app.app_context():
            scheduler.add_job(run_checks, 'interval',  max_instances=10, minutes=1)
            app.logger.info({"action":"registered_job"})
    scheduler.start()

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'
    return app
