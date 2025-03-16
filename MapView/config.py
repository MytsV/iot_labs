import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

STORE_HOST = os.environ.get("STORE_HOST") or "localhost"
STORE_PORT = os.environ.get("STORE_PORT") or 8000
