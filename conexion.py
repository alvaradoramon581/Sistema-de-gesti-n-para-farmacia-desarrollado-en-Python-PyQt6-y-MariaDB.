import mysql.connector
from mysql.connector import Error

from config import (
    DB_HOST,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)


def conectar():
    try:
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        if conexion.is_connected():
            return conexion

    except Error as e:
        print("Error al conectar con MariaDB:", e)
        return None