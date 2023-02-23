from flask_cors import CORS

def init(app) -> None:
    CORS(app, resources={r"/api/*": {"origins": "*"}})