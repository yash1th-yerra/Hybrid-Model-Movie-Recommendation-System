from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, bcrypt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)

    # Register Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.movies import bp as movies_bp
    app.register_blueprint(movies_bp)
    
    from app.recommendations import bp as rec_bp
    app.register_blueprint(rec_bp)

    @app.route('/')
    def index():
        return 'Movie Recommendation API V2 is Running!'

    return app
