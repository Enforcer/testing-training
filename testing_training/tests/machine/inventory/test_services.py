from sqlalchemy import create_engine

from testing_training.machine.database import Base, Session
from testing_training.machine.inventory.engine import Engine
from testing_training.machine.inventory.stock import Stock
from testing_training.machine.products.money import Currency, Money
from testing_training.machine.products.product import Product

from testing_training.machine.inventory.services import get_inventory, Entry


def test_returns_sum_of_quantities_per_product(tmp_path_factory) -> None:
    sqlite_file = tmp_path_factory.mktemp("db") / "test.db"
    engine = create_engine(f"sqlite:///{sqlite_file}")
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)

    session = Session()
    product_1 = Product(
        name="Pants",
        description="Irrelevant",
        price=Money(1, Currency.PLN),
        image=b"image",
    )
    product_2 = Product(
        name="Shirt",
        description="Irrelevant",
        price=Money(1, Currency.PLN),
        image=b"image",
    )
    session.add_all([product_1, product_2])
    session.flush()
    stock_1 = Stock(product_id=product_1.id, quantity=1)
    stock_2 = Stock(product_id=product_1.id, quantity=2)
    stock_3 = Stock(product_id=product_2.id, quantity=0)
    session.add_all([stock_1, stock_2, stock_3])
    session.flush()
    engines = [
        Engine(row=1, column=1, stock_id=stock_1.id),
        Engine(row=1, column=2, stock_id=stock_2.id),
        Engine(row=2, column=1, stock_id=None),
        Engine(row=2, column=2, stock_id=stock_3.id),
    ]
    session.add_all(engines)
    session.flush()

    inventory = get_inventory()

    assert len(inventory) == 2
    assert set(inventory) == {
        Entry(product_id=product_1.id, quantity=3),
        Entry(product_id=product_2.id, quantity=0),
    }
