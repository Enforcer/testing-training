from collections import defaultdict
from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class Item:
    name: str
    price: float


@dataclass
class Stocks:
    id: int
    item: Item
    quantity: int
    engine_id: str


## Results


class ItemUnavailable:
    pass


@dataclass(frozen=True)
class ItemSold:
    engine_to_move: str
    price: float


@dataclass
class OneOrMoreOfItemUnavailable:
    missing_item_names: list[str]


@dataclass
class ItemsSold:
    engines_to_move: list[str]
    price: float


class UnitVendingMachine:
    def __init__(self, stocks: list[Stocks]) -> None:
        all_stock_id = {stock.id for stock in stocks}
        if len(all_stock_id) != len(stocks):
            raise Exception("Duplicated stock ids")

        all_engine_ids = {stock.engine_id for stock in stocks}
        if len(all_engine_ids) != len(stocks):
            raise Exception("Each stock need to have unique engine!")

        self._stocks_by_id = {stock.id: stock for stock in stocks}

    def get_items_count(self, item_name: str) -> int:
        return sum(
            stock.quantity
            for stock in self._stocks_by_id.values()
            if stock.item.name == item_name
        )

    def buy(self, item_name: str) -> ItemSold | ItemUnavailable:
        for stock in self._stocks_by_id.values():
            if stock.item.name == item_name and stock.quantity > 0:
                stock.quantity -= 1
                return ItemSold(engine_to_move=stock.engine_id, price=stock.item.price)
        return ItemUnavailable()

    def buy_many(self, item_names: list[str]) -> OneOrMoreOfItemUnavailable | ItemsSold:
        missing_items = []

        stock_qty_delta = defaultdict(lambda: 0)
        for item_name in item_names:
            found = False
            for stock in self._stocks_by_id.values():
                stock_effective_qty = stock.quantity - stock_qty_delta[stock.id]
                if stock.item.name == item_name and stock_effective_qty > 0:
                    stock_qty_delta[stock.id] += 1
                    found = True
                    break

            if not found:
                missing_items.append(item_name)

        if missing_items:
            return OneOrMoreOfItemUnavailable(missing_item_names=missing_items)
        else:
            total = 0
            engines_to_move = []
            for stock_id, delta in stock_qty_delta.items():
                stock = self._stocks_by_id[stock_id]
                total += stock.item.price
                engines_to_move.append(stock.engine_id)
            return ItemsSold(engines_to_move=engines_to_move, price=total)


def test_duplicated_stock_ids() -> None:
    socks = Item(name="Socks", price=9)
    socks_stock_1 = Stocks(id=1, item=socks, quantity=10, engine_id="1")

    with pytest.raises(Exception):
        UnitVendingMachine(stocks=[socks_stock_1, socks_stock_1])


def test_duplicated_engine_ids() -> None:
    socks = Item(name="Socks", price=9)
    socks_stock_1 = Stocks(id=1, item=socks, quantity=2, engine_id="1")
    socks_stock_2 = Stocks(id=2, item=socks, quantity=2, engine_id="1")

    with pytest.raises(Exception):
        UnitVendingMachine(stocks=[socks_stock_1, socks_stock_2])


def test_buying_not_existing_items() -> None:
    socks = Item(name="Socks", price=9)
    shirt = Item(name="Shirt", price=10)
    socks_stock_1 = Stocks(id=1, item=socks, quantity=10, engine_id="1")
    socks_stock_2 = Stocks(id=2, item=socks, quantity=10, engine_id="2")
    shirt_stock = Stocks(id=3, item=shirt, quantity=5, engine_id="3")

    machine = UnitVendingMachine(stocks=[socks_stock_1, socks_stock_2, shirt_stock])

    result = machine.buy_many(["Dress", "Shoes"])

    assert isinstance(result, OneOrMoreOfItemUnavailable)
    assert result.missing_item_names == ["Dress", "Shoes"]
