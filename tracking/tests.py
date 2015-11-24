from decimal import Decimal
from collections import namedtuple

from django.test import TestCase

from authenticating.models import User
from tracking.models import Rate, Transaction


def to_decimal(amount, place='0.001'):
    return Decimal(amount).quantize(Decimal(place))


class RateTestCase(TestCase):
    def test_total_nothing(self):
        actual = Rate.objects.total()
        self.assertEqual(actual, 0)

    def test_total_something(self):
        instance = Rate()
        instance.description = 'Test Rate'
        instance.amount = Decimal(10)
        instance.days = 10
        instance.user = User.objects.create_user('test@yahoo.com')
        instance.save()

        actual = Rate.objects.total()
        self.assertEqual(actual, to_decimal(1))

    def test_calculate_amount_per_day(self):
        instance = Rate()
        instance.description = 'Test Rate'
        instance.amount = Decimal(10)
        instance.days = 10
        instance.user = User.objects.create_user('test@yahoo.com')
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.amount_per_day, Decimal(1))

    def test_calculate_round_amount_per_day(self):
        instance = Rate()
        instance.description = 'Test Rate'
        instance.amount = Decimal(10)
        instance.days = 11
        instance.user = User.objects.create_user('test@yahoo.com')
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.amount_per_day, to_decimal(0.909))

    def test_calculate_negative_amount_per_day(self):
        instance = Rate()
        instance.description = 'Test Rate'
        instance.amount = Decimal(-10)
        instance.days = 11
        instance.user = User.objects.create_user('test@yahoo.com')
        instance.save()
        instance.refresh_from_db()
        self.assertEqual(instance.amount_per_day, to_decimal(-0.909))


class TransactionTestCase(TestCase):
    def test_sum_nothing(self):
        actual = Transaction.objects.total()
        self.assertEqual(actual, 0)

    def test_sum_one(self):
        mock = Transaction()
        mock.amount = Decimal(10)
        mock.description = 'Test'
        mock.user = User.objects.create_user('test@yahoo.com')
        mock.save()

        actual = Transaction.objects.total()
        self.assertEqual(actual, to_decimal(10))

    def test_sum_two(self):
        mock = Transaction()
        mock.amount = Decimal(10)
        mock.description = 'Test'
        mock.user = User.objects.create_user('test@yahoo.com')
        mock.save()

        mock2 = Transaction()
        mock2.amount = Decimal(-5)
        mock2.description = 'Test'
        mock2.user = User.objects.create_user('another@yahoo.com')
        mock2.save()

        actual = Transaction.objects.total()
        self.assertEqual(actual, to_decimal(5))


class TransactRateBalanceTestCase(TestCase):
    def _create_user(self, name):
        create_user = User.objects.create_user
        user = create_user(email='{}@bennedetto.com'.format(name))
        user.save()
        setattr(self, name, user)

    def _associate_rates(self, name, rates):
        user = getattr(self, name)
        for item in rates:
            rate = Rate()
            rate.description = 'Test Rate'
            rate.amount = item.amount
            rate.days = item.days
            rate.user = user
            rate.save()

    def setUp(self):
        users = ['alex', 'kelly', 'sarah']
        rate = namedtuple('rate', 'amount days')
        rates = {'alex': [rate(10, 1), rate(-5, 4)],
                 'kelly': [rate(100, 30), rate(-10, 3)],
                 'sarah': [rate(10, 10), rate(5, 5)]}

        for name in users:
            self._create_user(name)

        for name, rates in rates.items():
            self._associate_rates(name, rates)

    def test_it(self):
        '''
        E2E: Transact Rate Balance
        Should open each user's day with a a transaction representing
        the total of all their rates
        '''
        users = User.objects.all()
        Transaction.objects.bulk_transact_rate_total(users)
        transactions = Transaction.objects.all()

        self.assertEqual(len(transactions), 3)  # assert counts
        for user in [self.alex, self.kelly, self.sarah]:
            self.assertEqual(len(transactions.user(user)), 1)

        for pair in [(self.alex, 8.75),  # assert totals
                     (self.kelly, 0.0),
                     (self.sarah, 2)]:
            user, total = pair
            actual = transactions.user(user).total()
            expected = to_decimal(total)
            self.assertEqual(actual, expected)
