from flask import Flask
from flask_cors import CORS
from config import Config
import os

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.tracking import tracking_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tracking_bp)
    
    return app
