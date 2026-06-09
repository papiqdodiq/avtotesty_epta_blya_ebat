import os
from dotenv import load_dotenv

load_dotenv()

class MoviesDbCreds:
    DATABASE_NAME = os.getenv('DBNAME')
    USERNAME = os.getenv('DB_USER')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')