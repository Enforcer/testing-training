import pytest
from sqlalchemy import create_engine
from testing_training.machine.database import Base, Session
from testing_training.machine.products.money import Currency, Money
from testing_training.machine.products.services import (
    add_product,
    list_products,
    DuplicateName,
)


def test_added_product_is_returned(tmp_path_factory) -> None:
    sqlite_file = tmp_path_factory.mktemp("db") / "test.db"
    engine = create_engine(f"sqlite:///{sqlite_file}")
    Base.metadata.create_all(engine)
    Session.remove()
    Session.configure(bind=engine)

    add_product(
        name="Socks",
        description="A pair of socks",
        price=Money(9, Currency.PLN),
        image=b"image",
    )

    products = list_products()

    assert len(products) == 1
    product = products[0]
    assert isinstance(product.id, int)
    assert product.name == "Socks"
    assert product.description == "A pair of socks"
    assert product.price == Money(9, Currency.PLN)


def test_cannot_add_two_products_with_the_same_name(tmp_path_factory) -> None:
    sqlite_file = tmp_path_factory.mktemp("db") / "test.db"
    engine = create_engine(f"sqlite:///{sqlite_file}")
    Base.metadata.create_all(engine)
    Session.remove()
    Session.configure(bind=engine)

    add_product(
        name="Dress",
        description="Nice and lightweight dress",
        price=Money(9, Currency.PLN),
        image=b"image",
    )

    with pytest.raises(DuplicateName):
        add_product(
            name="Dress",
            description="Nice and lightweight dress",
            price=Money(9, Currency.PLN),
            image=b"image",
        )
