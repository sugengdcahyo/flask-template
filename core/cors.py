from flask_cors import CORS

def init(app) -> None:
    ORIGINS = [
        "http://localhost:8000",
        "http://domain.com"
    ]
    CORS(app, origins=ORIGINS)