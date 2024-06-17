from pathlib import Path

from sqlalchemy import select

from testing_training.machine.inventory.engine import Engine
from testing_training.machine.inventory.stock import Stock
from testing_training.machine.products.money import Money, Currency
from testing_training.machine.buyer_app.order import Order
from testing_training.machine.products import add_product, list_products
from testing_training.machine.database import Base, Session, engine as db_engine


def main() -> None:
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)

    images_dir = Path(__file__).parent / "example_data"

    with Session() as session:
        session.execute(select(Order)).scalars().all()
        add_product(
            "Pure Still Water",
            "Experience the refreshing taste of Pure Still Water. Sourced from natural springs, our water is filtered to perfection, ensuring a crisp and clean flavor. Ideal for staying hydrated throughout the day, Pure Still Water is your perfect companion for work, exercise, or relaxation. Enjoy the essence of purity in every sip.",
            Money(3.59, Currency.PLN),
            (images_dir / "water.webp").read_bytes(),
        )
        add_product(
            "nErgize Isotonic Drink",
            "Boost your hydration and energy levels with Energize Isotonic Drink. Specially formulated to replenish electrolytes and provide quick energy, this drink is perfect for athletes and active individuals. Enjoy the refreshing taste and the benefits of enhanced performance and endurance.",
            Money(5.99, Currency.PLN),
            (images_dir / "isotonic.webp").read_bytes(),
        )
        add_product(
            "Pow3r Protein Bar",
            "Fuel your body with the delicious and nutritious Power Protein Bar. Packed with high-quality protein and essential nutrients, this bar is perfect for a post-workout snack or a quick meal on the go. Enjoy the satisfying taste and boost your energy and muscle recovery.",
            Money(5.49, Currency.PLN),
            (images_dir / "proteinbar.webp").read_bytes(),
        )
        add_product(
            "Crunchy Peantus",
            "Satisfy your cravings with our Crunchy Peanuts. These roasted and salted peanuts are packed with protein and essential nutrients, making them the perfect snack for any time of day. Enjoy the delicious taste and crunchiness that keeps you coming back for more.",
            Money(8.99, Currency.PLN),
            (images_dir / "peanuts.webp").read_bytes(),
        )

        products = list_products()

        water = next(
            product for product in products if product.name == "Pure Still Water"
        )
        isotonic = next(
            product for product in products if product.name == "nErgize Isotonic Drink"
        )
        protein_bar = next(
            product for product in products if product.name == "Pow3r Protein Bar"
        )
        peanuts = next(
            product for product in products if product.name == "Crunchy Peantus"
        )

        for row, column in zip([1] * 4, [1, 2, 3, 4]):
            stock = Stock(product_id=water.id, quantity=4)
            session.add(stock)
            session.flush()
            engine = Engine(row=row, column=column, stock_id=stock.id)
            session.add(engine)
            session.flush()

        for row, column in zip([2] * 4 + [3] * 4, [1, 2, 3, 4] * 2):
            stock = Stock(product_id=isotonic.id, quantity=4)
            session.add(stock)
            session.flush()
            engine = Engine(row=row, column=column, stock_id=stock.id)
            session.add(engine)
            session.flush()

        for row, column in zip([4] * 2, [1, 2]):
            stock = Stock(product_id=protein_bar.id, quantity=0)
            session.add(stock)
            session.flush()
            engine = Engine(row=row, column=column, stock_id=stock.id)
            session.add(engine)
            session.flush()

        for row, column in zip([4] * 2, [3, 4]):
            stock = Stock(product_id=peanuts.id, quantity=4)
            session.add(stock)
            session.flush()
            engine = Engine(row=row, column=column, stock_id=stock.id)
            session.add(engine)
            session.flush()

        session.commit()


if __name__ == "__main__":
    main()
