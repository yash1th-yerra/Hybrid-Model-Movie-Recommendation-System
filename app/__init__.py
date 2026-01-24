from flask import Flask
from .config import Config
from .extensions import db, migrate

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints (Placeholder for now)
    # from .main import bp as main_bp
    # app.register_blueprint(main_bp)

    @app.route('/')
    def index():
        return 'Movie Recommendation API V2 is Running!'

    return app
