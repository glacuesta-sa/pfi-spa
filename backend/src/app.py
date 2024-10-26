from flask import Flask
import route
from flask_cors import CORS # type: ignore
import debugpy # type: ignore
import debugger

# init debugger if needed
debugger.init()

print("Starting app.. . . .")

app = Flask(__name__)
CORS(app)

# Inicializar las rutas
route.init_routes(app)

if __name__ == "__main__":
    print("Starting app.. . . .")
    app.run(debug=True, host='0.0.0.0', port=80)
   
