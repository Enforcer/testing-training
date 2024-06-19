from dataclasses import dataclass
from decimal import Decimal

from hypothesis import given, strategies

from testing_training.machine.products import Money
from testing_training.machine.products.money import Currency


# See decimal strategy to generate numbers
# https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.decimals


def test_calculate_commission_loses_no_money() -> None:
    price = Money("100", Currency.USD)
    amount = 1

    result = calculate_commission(
        price=price,
        amount=amount,
        sell_commission=Decimal("0.2"),
    )

    value_without_commission = Money(round(price.amount * amount, 2), Currency.USD)
    commission = Money(0, Currency.USD)
    total_money_before = value_without_commission + commission
    total_money_after = result.payout + result.commission_for_platform
    assert total_money_before == total_money_after


@dataclass(frozen=True)
class Result:
    payout: Money
    commission_for_platform: Money


def calculate_commission(
    price: Money,
    amount: int,
    sell_commission: Decimal,
) -> Result:
    payout = round(price.amount * amount, 2)
    actual_payout = Money((Decimal(1) - sell_commission) * payout, Currency.USD)
    commission = Money(payout * sell_commission, Currency.USD)
    return Result(payout=actual_payout, commission_for_platform=commission)
