
import psycopg
import os
from psycopg import AsyncConnection
from dotenv import load_dotenv

load_dotenv()


async def get_connection():
    return await AsyncConnection.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="require"
    )