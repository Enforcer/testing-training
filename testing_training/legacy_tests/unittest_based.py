import unittest

from testing_training.machine.products.money import Money, Currency


class MoneySuite(unittest.TestCase):
    def test_multiply(self):
        money = Money(1, Currency.USD)

        money = money * 2

        assert money.amount == 2
        assert money.currency == Currency.USD
