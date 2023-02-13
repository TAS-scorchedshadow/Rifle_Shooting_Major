from flask import Flask, render_template

from app.shell_helper import clear_table
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth_bp.login"
mail = Mail()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    csrf.init_app(app)
    app.secret_key = app.config['SECRET_KEY']
    migrate.init_app(app, db)
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    ctx = app.app_context()
    ctx.push()

    register_blueprints(app)
    Talisman(app, content_security_policy=None, force_https=app.config['FORCE_HTTPS'])
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
    from app.error.views import error_bp

    app.register_blueprint(csrf.exempt(shell_bp))
    app.register_blueprint(csrf.exempt(time_convert_blueprint))

    app.register_blueprint(csrf.exempt(admin_bp))
    app.register_blueprint(csrf.exempt(api_bp))
    app.register_blueprint(csrf.exempt(auth_bp))

    app.register_blueprint(csrf.exempt(plotsheet_bp))
    app.register_blueprint(csrf.exempt(profile_bp))
    app.register_blueprint(csrf.exempt(upload_bp))

    app.register_blueprint(csrf.exempt(welcome_bp))
    app.register_blueprint(csrf.exempt(error_bp))


def configure_error_handlers(app):
    # Page not found
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    # Internal server error
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error/500.html'), 500

    # Unauthorised/Forbidden
    @app.errorhandler(403)
    def user_unauthorised(e):
        return render_template('error/403.html'), 403

def configure_shell_processor(app):
    from app.models import User, Stage, Shot, Club

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Stage': Stage, 'Shot': Shot, 'Club': Club}
