import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FACTURE_URL = os.getenv('FACTURE_URL', 'https://app.facture.com.mx')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), 'downloads')