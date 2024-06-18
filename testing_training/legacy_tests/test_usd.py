from testing_training.machine.products.money import Money, Currency


def test_usd():
    money = Money(10, Currency.USD)

    assert isinstance(money, Money)
    assert money.amount == 10
    assert money.currency == "USD"
