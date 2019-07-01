from main import app
from flask_cors import CORS
CORS(app, supports_credentials=True)

if __name__ == "__main__":
    app.run('0.0.0.0', port=8882)
