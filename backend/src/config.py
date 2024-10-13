import os
import boto3

# TODO read from AWS Systems Manager Parameter Store
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27018/')
MONDO_DB = 'mondo_db'
DEBUG_MODE = bool(int(os.getenv('FLASK_DEBUG', 0)))

# Variables de entorno para AWS S3
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_SECRET_ACCESS_TOKEN = os.getenv('AWS_SECRET_ACCESS_TOKEN')

# Configuración de cliente de boto3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_session_token=AWS_SECRET_ACCESS_TOKEN)