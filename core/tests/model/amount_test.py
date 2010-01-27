# Created By: Eric Mc Sween
# Created On: 2007-12-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import operator as op

from nose.tools import eq_, assert_raises

from hsutil.currency import CAD, EUR, PLN, USD, CZK
from hsutil.testcase import TestCase

from ...model.amount import format_amount, parse_amount, Amount

class AmountTest(TestCase): # don't clash the name with moneyguru.amount.Amount
    def test_auto_quantize(self):
        # Amounts are automatically set to 2 digits after the dot.
        eq_(Amount(1.11, CAD), Amount(1.111, CAD))
    
    def test_add(self):
        # Amounts can be added together, given that their currencies are the same.
        eq_(Amount(1, CAD) + Amount(2, CAD), Amount(3, CAD))
        assert_raises(ValueError, op.add, Amount(1, CAD), Amount(2, USD))

    def test_add_other_types(self):
        # You can't add something else to an amount and vice-versa.
        assert_raises(TypeError, op.add, Amount(1, CAD), 2)
        assert_raises(TypeError, op.add, 1, Amount(2, CAD))

    def test_add_zero(self):
        # It's possible to add 0 to an amount.
        eq_(Amount(1, CAD) + 0, Amount(1, CAD))
        eq_(0 + Amount(2, CAD), Amount(2, CAD))
        eq_(Amount(1, CAD) + Amount(0, USD), Amount(1, CAD))
        eq_(Amount(0, USD) + Amount(2, CAD), Amount(2, CAD))

    def test_cmp(self):
        # Amounts support inequalities with other amounts with the same currency.
        assert Amount(10, CAD) > Amount(9, CAD)
        assert Amount(10, CAD) >= Amount(9, CAD)
        assert not Amount(10, CAD) < Amount(9, CAD)
        assert not Amount(10, CAD) <= Amount(9, CAD)

    def test_cmp_with_zero(self):
        # Amounts are comparable to zero, but not any other number.
        assert Amount(42, CAD) > 0
        assert_raises(TypeError, op.gt, Amount(0, CAD), 42)
        assert Amount(42, CAD) >= 0
        assert_raises(TypeError, op.ge, Amount(0, CAD), 42)
        assert not Amount(42, CAD) < 0
        assert_raises(TypeError, op.lt, Amount(0, CAD), 42)
        assert not Amount(42, CAD) <= 0
        assert_raises(TypeError, op.le, Amount(0, CAD), 42)
    
    def test_cmp_with_zero_in_other_currency(self):
        # Amounts with different currencies are not comparable, even if one side is 0.
        assert_raises(ValueError, op.gt, Amount(42, CAD), Amount(0, USD))
        assert_raises(ValueError, op.ge, Amount(42, CAD), Amount(0, USD))
        assert_raises(ValueError, op.lt, Amount(42, CAD), Amount(0, USD))
        assert_raises(ValueError, op.le, Amount(42, CAD), Amount(0, USD))
    
    def test_div_with_amount(self):
        # Amounts can be divided by other amounts if they all amounts share the same currency. That
        # yields a plain number.
        eq_(Amount(1, CAD) / Amount(2, CAD), 0.5)
        assert_raises(ValueError, op.div, Amount(1, CAD), Amount(2, USD))

    def test_div_with_number(self):
        # Amounts can be divided by a number, yielding an amount.
        eq_(Amount(10, CAD) / 2, Amount(5, CAD))
        eq_(Amount(3, CAD) / 1.5, Amount(2, CAD))

    def test_div_number_with_amount(self):
        # You can't divide a number with an amount.
        assert_raises(TypeError, op.div, 10, Amount(3, CAD))

    def test_eq(self):
        # Amounts are equal if they have the same value and the same
        # currency. An amount with a value of zero is equal to 0. Any other
        # case yields non-equality.
        assert Amount(10, CAD) == Amount(10, CAD)
        assert not Amount(10, CAD) == Amount(11, CAD)
        assert not Amount(42, CAD) == Amount(42, USD)
        assert not Amount(10, CAD) != Amount(10, CAD)
        assert Amount(11, CAD) != Amount(10, CAD)
        assert Amount(42, CAD) != Amount(42, USD)

    def test_eq_other_type(self):
        # An amount is not equal to any other type (except in the zero case).
        assert not Amount(10, CAD) == 'foobar'
        assert not Amount(0, CAD) == 'foobar'

    def test_eq_zero(self):
        # An amount with a value of zero is equal to 0.
        assert Amount(0, CAD) == 0
        assert not Amount(0, CAD) == 42
        assert not Amount(42, CAD) == 0

    def test_float(self):
        # It's possible to convert an Amount with currency to float.
        eq_(float(Amount(42, USD)), 42)
    
    def test_immutable(self):
        # Amount is an immutable class (can't set currency).
        try:
            Amount(42, CAD).currency = 'foo'
        except AttributeError:
            pass # what should happen
        else:
            self.fail('It shouldn\'t be possible to set an Amount\'s currency')
    
    def test_init_with_float(self):
        # We don't have the same restriction as Decimal regarding initialization with floats.
        try:
            Amount(1.42, CAD)
        except TypeError:
            self.fail('Amount should be able to be created with floats')
    
    def test_mul_amount(self):
        # It doesn't make sense to multiply two amounts together.
        assert_raises(TypeError, op.mul, Amount(2, CAD), Amount(2, CAD))

    def test_mul_number(self):
        # It's possible to multiply an amount by a number.
        eq_(Amount(2, CAD) * 2, Amount(4, CAD))
        eq_(Amount(2, CAD) * 1.5, Amount(3, CAD))
        eq_(1.5 * Amount(2, CAD), Amount(3, CAD))

    def test_op(self):
        # Amount currency is preserved after an operation.
        eq_(-Amount(42, CAD), Amount(-42, CAD))
        eq_(abs(Amount(-42, CAD)), Amount(42, CAD))
        # This one is to make sure that __abs__ is overriden. __abs__ only seems to be called when
        # the starting numeral is positive.
        eq_(abs(Amount(42, CAD)), Amount(42, CAD))
        eq_(Amount(42, CAD) * 2, Amount(84, CAD))
        eq_(Amount(42, CAD) / 2, Amount(21, CAD))
    
    def test_op_float(self):
        # As opposed to Decimal, Amount allows operations with floats.
        eq_(Amount(42, CAD) * 2.0, Amount(84, CAD))
        eq_(Amount(42, CAD) / 2.0, Amount(21, CAD))
    
    def test_sub(self):
        # Amounts can be substracted one from another, given that their currencies are the same.
        eq_(Amount(10, CAD) - Amount(1, CAD), Amount(9, CAD))
        assert_raises(ValueError, op.sub, Amount(10, CAD), Amount(1, USD))

    def test_sub_other_type(self):
        # You can't subtract something else from an amount and vice-versa.
        assert_raises(TypeError, op.sub, Amount(10, CAD), 1)
        assert_raises(TypeError, op.sub, 10, Amount(1, CAD))

    def test_sub_zero(self):
        # It is possible to substract zero and from zero.
        eq_(Amount(2, CAD) - 0, Amount(2, CAD))
        eq_(0 - Amount(22, CAD), Amount(-22, CAD))
        eq_(Amount(0, USD) - Amount(22, CAD), Amount(-22, CAD))
        eq_(Amount(2, CAD) - Amount(0, USD), Amount(2, CAD))


class ParseAmount(TestCase):
    def test_comma_as_decimal_sep(self):
        # commas are correctly parsed when used instead of a dot for decimal separators.
        eq_(parse_amount('54,67', USD) , Amount(54.67, USD))
    
    def test_comma_as_grouping_sep(self):
        # When a comma is used as a grouping separator, it doesn't prevent the number from being read.
        eq_(parse_amount('1,454,67', USD) , Amount(1454.67, USD))
        eq_(parse_amount('CZK 3,000.00', USD) , Amount(3000, CZK))
        eq_(parse_amount('CZK 3 000.00', USD) , Amount(3000, CZK))
    
    def test_currency(self):
        # Prefixing or suffixing the amount with a currency ISO code sets the currency attr of the
        # amount.
        eq_(parse_amount('42.12 eur'), Amount(42.12, EUR))
        eq_(parse_amount('eur42.12'), Amount(42.12, EUR))
    
    def test_currency_not_in_list(self):
        # If the currency is not in the list, the amount is invalid.
        assert_raises(ValueError, parse_amount, '42.12 foo')
    
    def test_currency_and_garbage(self):
        # If there is garbage in addition to the currency, the whole amount is invalid.
        assert_raises(ValueError, parse_amount, '42.12 cadalala')
    
    def test_division_result_in_a_float(self):
        # Dividing an amount by another amount gives a float.
        eq_(parse_amount('1 / 2 CAD'), Amount(0.5, CAD))
    
    def test_empty(self):
        eq_(parse_amount(''), 0)
        eq_(parse_amount(' '), 0)
        eq_(parse_amount(None), 0)
    
    def test_expressions(self):
        eq_(parse_amount('18 + 24 CAD'), Amount(42, CAD))
        eq_(parse_amount('56.23 - 13.99 USD'), Amount(42.24, USD))
        eq_(parse_amount('21 * 4 / (1 + 1) EUR'), Amount(42, EUR))
    
    def test_garbage_around(self):
        # Amounts with garbage around them can still be parsed.
        eq_(parse_amount('$10.42', USD, False), Amount(10.42, USD))
        eq_(parse_amount('foo10bar', USD, False), Amount(10.00, USD))
        eq_(parse_amount('$.42', USD, False), Amount(0.42, USD))
    
    def test_invalid(self):
        assert_raises(ValueError, parse_amount, 'asdf')
        assert_raises(ValueError, parse_amount, '+-.')
        try:
            assert_raises(ValueError, parse_amount, 'open(\'some_important_file\').read()')
        except IOError:
            self.fail('Something is very wrong with parse_amount. You must *not* perform an eval on a string like this.')
    
    def test_quote_as_grouping_sep(self):
        # an amount using quotes as grouping sep is correctly parsed.
        eq_(parse_amount('1\'234.56', USD), Amount(1234.56, USD))
    
    def test_simple_amounts(self):
        eq_(parse_amount('1 EUR'), Amount(1, EUR))
        eq_(parse_amount('1.23 CAD'), Amount(1.23, CAD))
        eq_(parse_amount('1.234 PLN'), Amount(1.23, PLN))
    
    def test_space_as_thousand_sep(self):
        # When a space is used as a thousand separator, it doesn't prevent the number from being read.
        eq_(parse_amount('1 454,67', USD) , Amount(1454.67, USD))
    
    def test_zero(self):
        eq_(parse_amount('0'), 0)
    
    def test_zero_prefixed(self):
        # Parsing an amount prefixed by a zero does not result in it being interpreted as an octal
        # number.
        eq_(parse_amount('0200+0200 PLN'), Amount(400, PLN))
    
    def test_zero_after_dot(self):
        # A 0 after a dot dot not get misinterpreted as an octal prefix.
        eq_(parse_amount('.02 EUR'), Amount(.02, EUR))
    

class FormatAmount(TestCase):
    def test_blank_zero(self):
        # When blank_zero is True, 0 is rendered as an empty string.
        eq_(format_amount(0, blank_zero=True), '')
        eq_(format_amount(Amount(0.00, CAD), blank_zero=True), '')
        eq_(format_amount(Amount(12, CAD), blank_zero=True), 'CAD 12.00')
    
    def test_decimal_sep(self):
        # It's possible to specify an alternate decimal separator
        eq_(format_amount(Amount(12.34, CAD), CAD, decimal_sep=','), '12,34')
    
    def test_default_currency(self):
        # If the amount currency matches default_currency, the currency is not shown.
        eq_(format_amount(Amount(12.34, CAD), default_currency=CAD), '12.34')
        eq_(format_amount(Amount(12.34, CAD), default_currency=USD), 'CAD 12.34')
    
    def test_dot_grouping_sep_and_comma_decimal_sep(self):
        # Previously, there was a bug causing comma to be placed everywhere
        eq_(format_amount(Amount(1234.99, CAD), CAD, grouping_sep='.', decimal_sep=','), '1.234,99')
    
    def test_grouping_sep(self):
        # It's possible to specify an alternate grouping separator
        eq_(format_amount(Amount(12.99, CAD), CAD, grouping_sep=' '), '12.99')
        eq_(format_amount(Amount(1234.99, CAD), CAD, grouping_sep=' '), '1 234.99')
        eq_(format_amount(Amount(1234567.99, CAD), CAD, grouping_sep=' '), '1 234 567.99')
        eq_(format_amount(Amount(1234567890.99, CAD), CAD, grouping_sep=' '), '1 234 567 890.99')
    
    def test_negative_with_grouping(self):
        # Grouping separation ignore the negative sign
        eq_(format_amount(Amount(-123.45, CAD), CAD, grouping_sep=','), '-123.45') # was -,123.45
    
    def test_none(self):
        # When None is given, return ''.
        eq_(format_amount(None), '')
    
    def test_standard(self):
        # The normal behavior is to show the amount and the currency.
        eq_(format_amount(Amount(33, USD)), 'USD 33.00')

    def test_zero(self):
        # Zero is always shown without a currency, except if zero_currency is not None.
        eq_(format_amount(0), '0.00')
        eq_(format_amount(Amount(0, CAD)), '0.00')
        eq_(format_amount(Amount(0, USD), default_currency=CAD), '0.00')
        eq_(format_amount(0, default_currency=CAD, zero_currency=EUR), 'EUR 0.00')
        eq_(format_amount(0, default_currency=EUR, zero_currency=EUR), '0.00')
    
