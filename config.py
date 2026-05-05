import os
from dotenv import load_dotenv

# Load local .env file (ignored in Railway)
load_dotenv()

class Config:
    # Database URL (Railway or local)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Secret key for sessions
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")