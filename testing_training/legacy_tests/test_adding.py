from testing_training.machine.products.money import Currency, Money


class TestAdding:
    def check_adding_money(self) -> None:
        money_1 = Money(1, Currency.USD)
        money_2 = Money(5, Currency.USD)

        result = money_1 + money_2

        assert result.amount == 6
        assert result.currency == Currency.USD

    def check_0_can_be_added(self) -> None:
        money = Money(1, Currency.USD)

        result = money + 0

        assert result.amount == 1
        assert result.currency == Currency.USD
        assert result == money

    def check_it_can_be_added_to_0(self) -> None:
        money = Money(1, Currency.USD)

        result = 0 + money

        assert result.amount == 1
        assert result.currency == Currency.USD
        assert result == money
