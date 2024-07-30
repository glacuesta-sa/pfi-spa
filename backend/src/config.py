import os


MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27018/')
DATABASE_NAME = 'mondo_db'