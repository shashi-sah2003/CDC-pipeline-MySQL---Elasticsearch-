from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import time
from sqlalchemy.exc import OperationalError

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:root@db:3306/cdc_db_elasticsearch"

def get_db_connection(max_retries=5, retry_interval=5):
    for i in range(max_retries):
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
            engine.connect()
            return engine
        except OperationalError as e:
            if i == max_retries - 1:
                raise e
            print(f"Database connection attempt {i + 1} failed. Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)

engine = get_db_connection()

db: Session = Session(bind=engine)

def close_conn(db: Session) -> None:
    db.close()