from create_db import create_db
from models import create_tables, engine

if __name__ == '__main__':
    create_db()
    create_tables(engine)
