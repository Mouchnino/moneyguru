# Created On: 2010-04-17
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# This is a reference implementation for the amount.c module

from __future__ import division

import operator

from hscommon.currency import Currency

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
    def __init__(self, value, currency, _value_is_shifted=False):
        """Create an amount.

        The _value_is_shifted argument is for internal use."""
        assert isinstance(currency, Currency)     # This is just to make sure nobody sends a string.
        if _value_is_shifted:
            self._shifted_value = value
            self._value = value / 10 ** currency.exponent
        else:
            self._shifted_value = int(round(value * 10 ** currency.exponent))
            self._value = value
        self._currency = currency
    
    __slots__ = ['_value', '_shifted_value', '_currency']
    
    def __nonzero__(self):
        return bool(self._shifted_value)
    
    def __float__(self):
        return float(self.value)
    
    def __repr__(self):
        return 'Amount(%.*f, %r)' % (self.currency.exponent, self.value, self.currency)
    
    def __eq__(self, other):
        if other == 0:
            return self._shifted_value == 0
        elif isinstance(other, Amount):
            if self._currency == other._currency:
                return self._shifted_value == other._shifted_value
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
        return Amount(-self._shifted_value, self.currency, _value_is_shifted=True)

    def __abs__(self):
        return Amount(abs(self._shifted_value), self.currency, _value_is_shifted=True)

    def __add__(self, other):
        if self == 0:
            return other
        elif other == 0:
            return self
        elif isinstance(other, Amount):
            if self._currency == other._currency:
                return Amount(self._shifted_value + other._shifted_value, self._currency, _value_is_shifted=True)
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
                return Amount(self._shifted_value - other._shifted_value, self._currency, _value_is_shifted=True)
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
            return Amount(int(round(self._shifted_value * other)), self._currency, _value_is_shifted=True)

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        if isinstance(other, Amount):
            if self._currency != other._currency:
                raise ValueError('Cannot coerce amounts of currency %s and %s' % (self.currency, other.currency))
            return self.value / other.value
        else:
            return Amount(int(round(self._shifted_value / other)), self._currency, _value_is_shifted=True)

    @property
    def currency(self):
        return self._currency

    @property
    def value(self):
        return self._value
    
