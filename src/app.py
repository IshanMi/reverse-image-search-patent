import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()
template_folder = os.getenv("TEMPLATES_FOLDER")

app = Flask(__name__, template_folder=template_folder)
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['DOWNLOAD_FOLDER'] = os.getenv("DOWNLOAD_FOLDER")
app.config['CELERY_BROKER_URL'] = os.getenv("BROKER_URL")
app.config['CELERY_BACKEND_URL'] = os.getenv("BACKEND_URL")
app.config['IMAGES_FOLDER'] = os.getenv("IMAGES_FOLDER")
app.static_folder = os.getenv("STATIC_FOLDER")
