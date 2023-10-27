import os
import psycopg2

from db_files.configdb import DB_NAME, password, user


def create_db() -> None:
    connection = psycopg2.connect(
        database='postgres',
        user=user,
        password=password
    )
    connection.autocommit = True

    with connection.cursor() as cur:
        cur.execute(f"SELECT exists(SELECT datname FROM pg_catalog.pg_database "
                    f"WHERE lower(datname) = lower('{DB_NAME}'));")
        exists = cur.fetchone()
        match exists:
            case (False, ):
                cur.execute(f'CREATE DATABASE {DB_NAME};')
                print(f"Database {DB_NAME} has been created successfully")
            case (True, ):
                print(f"Database {DB_NAME} exists")
    connection.close()

if __name__ == '__main__':
    create_db()
