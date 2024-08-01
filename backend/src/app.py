from flask import Flask
from routes import init_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Inicializar las rutas
init_routes(app)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
