from flask import Flask
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


app = Flask(__name__)
db = SQLAlchemy()
csrf=CSRFProtect()
bootstrap= Bootstrap()
login_manager= LoginManager()
mail=Mail()

from .views import page
from .models import User, Task


def create_app(config):
    app.config.from_object(config)

    csrf.init_app(app)

    if not app.config.get('TEST', False):
        bootstrap.init_app(app)

    app.app_context().push()

    login_manager.init_app(app)
    login_manager.login_view='.login'

    mail.init_app(app)

    app.register_blueprint(page)

    with app.app_context():
        db.init_app(app)
        db.create_all()

    return app