from flask import Flask
import click
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
csrf = CSRFProtect()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return "Not Found", 404

    @app.errorhandler(500)
    def internal_error(error):
        return "Internal Server Error", 500

    @app.cli.command("init-db")
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized.")

    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument('password')
    def create_user(username, password):
        """Create a new user."""
        from models import User
        if User.query.filter_by(username=username).first():
            print(f"User {username} already exists.")
            return
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"User {username} created.")

    return app
