import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


def _env_flag(name):
    return os.environ.get(name, 'false').lower() == 'true'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(basedir, 'vowmotors.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(basedir, 'vowapp', 'static', 'uploads', 'vehicles')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB per request
    MAX_PHOTOS_PER_VEHICLE = 20

    DEALERSHIP_NAME = os.environ.get('DEALERSHIP_NAME', 'Vow Motors')

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    PASSWORD_RESET_MAX_AGE = 3600  # seconds a reset link stays valid

    # Production-only switches; leave unset locally so http://127.0.0.1 login keeps working.
    SESSION_COOKIE_SECURE = _env_flag('SECURE_COOKIES')
    REMEMBER_COOKIE_SECURE = _env_flag('SECURE_COOKIES')
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SAMESITE = 'Lax'
    BEHIND_PROXY = _env_flag('BEHIND_PROXY')
