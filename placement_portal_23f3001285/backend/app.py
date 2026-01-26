from flask import Flask, app
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.models import db
from backend.routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    
    from backend.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    from backend.routes.company import company_bp
    app.register_blueprint(company_bp, url_prefix="/company")


    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return {
            "status": "Placement Portal API running",
            "version": "v2"
        }
    
    return app


