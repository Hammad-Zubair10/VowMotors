from datetime import datetime

from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from .extensions import db, login_manager, csrf, mail, limiter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if app.config['BEHIND_PROXY']:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'dealer.login'
    login_manager.login_message = 'Please log in to access the dealer portal.'
    login_manager.login_message_category = 'error'
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    from .main.routes import main_bp
    from .dealer.routes import dealer_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(dealer_bp, url_prefix='/dealer')

    @app.context_processor
    def inject_globals():
        return {
            'dealership_name': app.config['DEALERSHIP_NAME'],
            'current_year': datetime.utcnow().year,
        }

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        from flask import flash, redirect, request
        flash('Too many attempts. Please wait a while and try again.', 'error')
        return redirect(request.path), 302

    @app.errorhandler(413)
    def too_large(e):
        from flask import flash, redirect, request
        flash('That upload was too large. Please use smaller image files.', 'error')
        return redirect(request.referrer or '/'), 302

    with app.app_context():
        db.create_all()

    return app
