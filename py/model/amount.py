# Unit Name: moneyguru.model.amount
# Created By: Eric Mc Sween
# Created On: 2007-12-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
from __future__ import division

import operator
import re
from itertools import groupby

from hsutil.currency import Currency

# The dash "-" has to be escaped even in []
re_expression = re.compile(r'^[+\-*/()\d\s.]*$')
# A zero not preceeded by a numeric character or dot and followed by a numeric character
re_octal_zero = re.compile(r'(?<![\d.,\w])0(?=\d)')
# 3 letters (capturing)
re_currency = re.compile(r'([a-zA-Z]{3})')
# grouping separator. a dot that has digit before and after *if* the right part is separated by a dot
re_grouping_sep = re.compile(r'(?<=[\d.])\.(?=\d+?\.\d)')

def cmp_wrap(op):
    def wrapper(self, other):
        if isinstance(other, Amount):
            if self.currency == other.currency:
                return op(self._value, other._value)
            else:
                raise ValueError("Can't coerce amounts of currency %s and %s" % (self.currency, other.currency))
        elif other == 0:
            return op(self._value, 0)
        else:
            raise TypeError("Can't compare an amount with a %r" % other.__class__.__name__)
    return wrapper


class Amount(object):
    """A class to store money amounts
    
    Amounts have a currency attribute, which can be None.
    When created, all Amounts are rounded to 2 digits.
    Arithmetic operations can't be performed between Amount of different currencies (even between
    None and not-None amounts). However, if the other part of the operation is not an Amount, it's ok
    (such as when you want to multiply by a float rate).
    Comparison rules (==, !=)
    - An amount is equal to another amount if their values and currencies match
    - An amount with a value of 0 is equal to 0
    Comparison rules (<, <=, >, >=):
    - When comparing 2 Amounts, if the currencies are different, raise ValueError.
    - When comparing Amount with another type, raise TypeError.
    - Special case: amounts can be compared with 0
    """    
    def __init__(self, value, currency, _convert_value=True):
        """Create an amount.

        The _convert_value argument is for internal use."""
        assert isinstance(currency, Currency)     # This is just to make sure nobody sends a string.
        self._value = int(round(value * 10 ** currency.exponent)) if _convert_value else value
        self._currency = currency
    
    __slots__ = ['_value', '_currency']
    
    def __nonzero__(self):
        return bool(self._value)
    
    def __float__(self):
        return self.value
    
    def __str__(self):
        return format_amount(self)
    
    def __repr__(self):
        return 'Amount(%.*f, %r)' % (self.currency.exponent, self.value, self.currency)
    
    def __eq__(self, other):
        if other == 0:
            return self._value == 0
        elif isinstance(other, Amount):
            if self._currency == other._currency:
                return self._value == other._value
            else:
                return False
        else:
            return NotImplemented

    def __ne__(self, other):
        return not self == other
        
    __lt__ = cmp_wrap(operator.lt)
    __le__ = cmp_wrap(operator.le)
    __gt__ = cmp_wrap(operator.gt)
    __ge__ = cmp_wrap(operator.ge)
    
    def __neg__(self):
        return Amount(-self._value, self.currency, _convert_value=False)

    def __abs__(self):
        return Amount(abs(self._value), self.currency, _convert_value=False)

    def __add__(self, other):
        if self == 0:
            return other
        elif other == 0:
            return self
        elif isinstance(other, Amount):
            if self._currency == other._currency:
                return Amount(self._value + other._value, self._currency, _convert_value=False)
            else:
                raise ValueError('Cannot coerce amounts of currency %s and %s' % (self.currency, other.currency))
        else:
            return NotImplemented

    def __sub__(self, other):
        if self == 0:
            return -other
        elif other == 0:
            return self
        elif isinstance(other, Amount):
            if self._currency == other._currency:
                return Amount(self._value - other._value, self._currency, _convert_value=False)
            else:
                raise ValueError('Cannot coerce amounts of currency %s and %s' % (self.currency, other.currency))
        else:
            return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return NotImplemented

    def __rsub__(self, other):
        if other == 0:
            return -self
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Amount):
            raise TypeError("Can't multiply two amounts together")
        else:
            return Amount(int(round(self._value * other)), self._currency, _convert_value=False)

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        if isinstance(other, Amount):
            if self._currency != other._currency:
                raise ValueError('Cannot coerce amounts of currency %s and %s' % (self.currency, other.currency))
            return self.value / other.value
        else:
            return Amount(int(round(self._value / other)), self._currency, _convert_value=False)

    @property
    def currency(self):
        return self._currency

    @property
    def value(self):
        return self._value / 10 ** self._currency.exponent


def format_amount(amount, default_currency=None, blank_zero=False, zero_currency=None, 
                  decimal_sep='.', grouping_sep=''):
    if amount is None:
        return ''
    number = '0.00'
    currency = None
    negative = False
    if not amount:
        if blank_zero:
            return ''
        elif zero_currency is not None and zero_currency != default_currency:
            currency = zero_currency.code
    else:
        negative = amount < 0
        number = '%.*f' % (amount.currency.exponent, float(abs(amount)))
        if amount.currency != default_currency:
            currency = amount.currency.code
    if decimal_sep != '.':
        number = number.replace('.', decimal_sep)
    if grouping_sep:
        # Yup, this code is complicated, but grouping digits *is* complicated.
        splitted = number.split(decimal_sep)
        left = splitted[0]
        groups = []
        for _, pair_group in groupby(enumerate(reversed(left)), lambda pair: pair[0] // 3):
            groups.append(''.join(reversed([pair[1] for pair in pair_group])))
        splitted[0] = grouping_sep.join(reversed(groups))
        number = decimal_sep.join(splitted)
    if negative:
        number = '-' + number
    if currency is not None:
        number = '%s %s' % (currency, number)
    return number

def parse_amount(string, default_currency=None, with_expression=True):
    # set 'with_expression' to False when you know 'string' doesn't contain any. It speeds up parsing
    if string is None or not string.strip():
        return 0
    
    currency = None
    m = re_currency.search(string)
    if m is not None:
        capture = m.group(0).upper()
        try:
            currency = Currency(capture)
        except ValueError:
            pass
        else:
            string = re_currency.sub('', string)
    currency = currency or default_currency
    
    if with_expression:
        string = string.replace(' ', '')
        string = re_octal_zero.sub('', string)
        if re_expression.match(string) is None:
            # These below are rare cases. It should not waste CPU every time parsing goes on.
            string = string.replace(',', '.')
            string = re_grouping_sep.sub('', string)
            if re_expression.match(string) is None:
                raise ValueError('Invalid expression %r' % string)
        try:
            value = eval(string)
        except SyntaxError:
            raise ValueError('Invalid expression %r' % string)
    else:
        value = float(string)
    if value == 0:
        return 0
    elif currency is not None:
        return Amount(value, currency)
    else:
        raise ValueError('No currency given')


def convert_amount(amount, target_currency, date):
    # Using private Amount attr and avoid using _convert_value is done for optimization purposes
    # The speedup is non-negligeable.
    if amount == 0 or amount._currency == target_currency:
        return amount
    exchange_rate = amount.currency.value_in(target_currency, date)
    return Amount(int(round(amount._value * exchange_rate)), target_currency, _convert_value=False)
