from src import create_app
import os

if __name__=='__main__':
    app = create_app()
    app.run(
        host=os.environ.get("FLASK_HOST", '0.0.0.0'),
        port=os.environ.get("FLASK_PORT", '1234')
    )
else:
    app = create_app()