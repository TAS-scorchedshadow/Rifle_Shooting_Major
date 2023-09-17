import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FORCE_HTTPS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_DISABLED = False  # Enable this to avoid having to login
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # or other relevant config var
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SESSION_COOKIE_SECURE = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    WTF_CSRF_ENABLED = False

    SEASON_START = os.environ.get('SEASON_START')
    SEASON_END = os.environ.get('SEASON_END')
