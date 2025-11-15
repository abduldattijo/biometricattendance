"""
Main Flask Application for Face Recognition Attendance System
Optimized for West African employees
"""
from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from models import db
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Import routes
from routes.dashboard import dashboard_bp
from routes.enrollment import enrollment_bp
from routes.attendance import attendance_bp


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Initialize directories
    config_class.init_app()

    # Setup logging
    setup_logging(app)

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(enrollment_bp, url_prefix='/enroll')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')

    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")

    # Favicon route
    @app.route('/favicon.ico')
    def favicon():
        return '', 204  # No Content response

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    app.logger.info("Face Recognition Attendance System initialized")

    return app


def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Create logs directory if it doesn't exist
        log_dir = Config.LOGS_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler
        file_handler = RotatingFileHandler(
            log_dir / 'app.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Face Recognition Attendance System startup')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
