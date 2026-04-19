import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    DB_USER = os.environ.get('DB_USER', 'pfm_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'pfm_pass_3r2e3fr2efefwqeefeffe')
    DB_HOST = os.environ.get('DB_HOST', '192.168.15.254')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'pyfinance')
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
