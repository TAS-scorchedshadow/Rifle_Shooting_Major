from flask import Flask, render_template

from app.shell_helper import clear_table
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_talisman import Talisman
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth_bp.login"
mail = Mail()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.secret_key = app.config['SECRET_KEY']
    csrf.init_app(app)
    migrate.init_app(app, db)
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    ctx = app.app_context()
    ctx.push()

    register_blueprints(app)
    Talisman(app, content_security_policy=None)
    configure_error_handlers(app)
    configure_shell_processor(app)

    return app


def register_blueprints(app):
    from app.time_convert import time_convert_blueprint
    from app.shell_helper import shell_bp

    from app.admin.views import admin_bp
    from app.api.api import api_bp
    from app.auth.views import auth_bp

    from app.plotsheet.views import plotsheet_bp
    from app.profile.views import profile_bp
    from app.upload.views import upload_bp

    from app.welcome.views import welcome_bp

    app.register_blueprint(shell_bp)
    app.register_blueprint(time_convert_blueprint)

    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)

    app.register_blueprint(plotsheet_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(upload_bp)

    app.register_blueprint(welcome_bp)


def configure_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error/500.html'), 500


def configure_shell_processor(app):
    from app.models import User, Stage, Shot

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Stage': Stage, 'Shot': Shot}
