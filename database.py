import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

print("Looking for:", ENV_FILE)
print("Exists:", ENV_FILE.exists())

load_dotenv(dotenv_path=ENV_FILE, override=True)

print("DB_HOST:", repr(os.getenv("DB_HOST")))
print("DB_USER:", repr(os.getenv("DB_USER")))
print("DB_NAME:", repr(os.getenv("DB_NAME")))


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


if __name__ == "__main__":
    try:
        db = get_connection()

        if db.is_connected():
            print("✅ MySQL database connected successfully!")

        db.close()

    except Exception as e:
        print("❌ MySQL connection failed!")
        print("Error:", e)