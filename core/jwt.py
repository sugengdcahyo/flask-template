from flask_jwt_extended import JWTManager
import os

def init(app) -> None:
    from datetime import timedelta
    app.config["JWT_SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["JWT_ALGORITHM"] = "HS256"
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=3600)
    # jwt.init_app(app)
    JWTManager(app)