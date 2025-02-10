import time
from sqlalchemy.exc import OperationalError

from database.models import Base
from database.conn import engine, db, close_conn
from database.crud import add_product


def initialize_database():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            Base.metadata.create_all(bind=engine)
            return True
        except OperationalError as e:
            retry_count += 1
            if retry_count == max_retries:
                raise e
            print(f"Failed to initialize database. Retrying in 5 seconds... ({retry_count}/{max_retries})")
            time.sleep(5)

def generate_product(i: int) -> dict:
    return {"name": f"product-{i}", "quantity": i}


def add_products() -> None:
    counter: int = 0

    while counter < 60:
        try:
            product: dict = generate_product(counter)
            add_product(db=db, product=product)
            print(f"product-{counter} inserted")
            time.sleep(2)
            counter += 1
        except Exception as e:
            print(f"Error adding product: {e}")
            time.sleep(2)

if __name__ == "__main__":
    try:
        initialize_database()
        add_products()
    finally:
        close_conn(db=db)