import os

# TODO read from AWS Systems Manager Parameter Store
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27018/')
MONDO_DB = 'mondo_db'
DEBUG_MODE = bool(int(os.getenv('FLASK_DEBUG', 0)))