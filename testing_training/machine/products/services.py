from sqlalchemy.exc import IntegrityError

from testing_training.machine.database import Session
from testing_training.machine.products.money import Money
from testing_training.machine.products.product import Product


class DuplicateName(Exception):
    pass


def add_product(name: str, description: str, price: Money, image: bytes) -> None:
    session = Session()
    product = Product(name=name, description=description, price=price, image=image)
    session.add(product)
    try:
        session.flush()
    except IntegrityError as e:
        session.rollback()
        raise DuplicateName from e


def list_products() -> list[Product]:
    session = Session()
    return session.query(Product).all()
