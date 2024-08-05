import os
from flask import Flask
from routes import init_routes
from flask_cors import CORS
import debugpy
import config

DEBUG_MODE = bool(int(os.getenv('FLASK_DEBUG', 0)))

print ("Debug Mode is enabled? " + str(DEBUG_MODE))
if DEBUG_MODE:
    debugpy.listen(("0.0.0.0", 5001))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()

app = Flask(__name__)
CORS(app)

# Inicializar las rutas
init_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
   
