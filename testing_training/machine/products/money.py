from decimal import Decimal
from enum import StrEnum
from typing import Self


class Currency(StrEnum):
    PLN = "PLN"


class Money:
    def __init__(self, amount: Decimal | int | float, currency: Currency | str) -> None:
        self._currency = Currency(currency)

        if isinstance(amount, float):
            amount = Decimal(str(amount))
        else:
            amount = Decimal(amount)

        quantized = amount.quantize(Decimal("0.01"))
        if amount != quantized:
            raise ValueError("Amount has to have at most two decimal places")
        self._amount = quantized

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._currency

    def __composite_values__(self) -> tuple[Decimal, str]:
        return self.amount, self.currency

    def __repr__(self) -> str:
        return f'Money(Decimal("{self.amount}"), {type(self.currency).__name__}.{self.currency})'

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            raise TypeError
        return self.amount == other.amount and self.currency == other.currency

    def __mul__(self, other: object) -> Self:
        if not isinstance(other, int):
            raise TypeError(
                f"can't multiply {type(self).__name__} by non-int of type '{type(other).__name__}'"
            )
        return type(self)(self.amount * other, self.currency)

    def __add__(self, other: object) -> Self:
        match other:
            case Money(amount=amount, currency=self.currency):
                return type(self)(self.amount + amount, self.currency)
            case Money(currency=_):
                raise ValueError(
                    f"cannot add {self} to {other} because of different currency"
                )
            case 0:
                return self
            case _:
                raise TypeError(
                    f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
                )

    def __radd__(self, other: object) -> Self:
        return self.__add__(other)
