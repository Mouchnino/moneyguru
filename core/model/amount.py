# Created By: Eric Mc Sween
# Created On: 2007-12-13
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

import re
from itertools import groupby

from hsutil.currency import Currency

from _amount import Amount

# The dash "-" has to be escaped even in []
re_expression = re.compile(r'^[+\-*/()\d\s.]*$')
# A zero not preceeded by a numeric character or dot and followed by a numeric character
re_octal_zero = re.compile(r'(?<![\d.,\w])0(?=\d)')
# 3 letters (capturing)
re_currency = re.compile(r'([a-zA-Z]{3})')
# grouping separator. a [.\s,'] that has digit before and after *if* the right part is separated by a dot
re_grouping_sep = re.compile(r"(?<=[\d.])[.\s,'](?=\d+?\.\d)")
# A valid amount
re_amount = re.compile(r"\d+\.\d+|\.\d+|\d+")

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

def parse_amount(string, default_currency=None, with_expression=True, auto_decimal_place=False):
    # set 'with_expression' to False when you know 'string' doesn't contain any. It speeds up parsing
    # Note that auto_decimal_place has no effect is the string is an expression (it would be too
    # complicated to implement for nothing)
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
    string = string.strip()
    string = string.replace(',', '.')
    string = re_grouping_sep.sub('', string)
    # isdigit means that it's not an expression and there's not '.' in it
    if auto_decimal_place and string.isdigit():
        place = currency.exponent if currency is not None else 2
        if place:
            string = string.rjust(place, '0')
            string = string[:-place] + '.' + string[-place:]
            with_expression = False
    if with_expression:
        string = string.replace(' ', '')
        string = re_octal_zero.sub('', string)
        if re_expression.match(string) is None:
            raise ValueError('Invalid expression %r' % string)
        try:
            value = eval(string)
        except SyntaxError:
            raise ValueError('Invalid expression %r' % string)
    else:
        try:
            value = float(string)
        except ValueError:
            # There might be some crap around the amount. Remove it and try again.
            m = re_amount.search(string)
            if m is None:
                raise ValueError("'{0}' is not an amount".format(string))
            value = float(string[m.start():m.end()])
    if value == 0:
        return 0
    elif currency is not None:
        return Amount(value, currency)
    else:
        raise ValueError('No currency given')


def convert_amount(amount, target_currency, date):
    if amount == 0:
        return amount
    currency = amount.currency
    if currency == target_currency:
        return amount
    exchange_rate = currency.value_in(target_currency, date)
    return Amount(amount.value * exchange_rate, target_currency)

def prorate_amount(amount, spread_over_range, wanted_range):
    """Returns the prorated part of `amount` spread over `spread_over_range`, for the `wanted_range`.
    
    For example, if 100$ are spead over a range that lasts 10 days and that there's an overlap of 4
    days between `spread_over_range` and `wanted_range`, the result will be 40$.
    """
    if not spread_over_range:
        return 0
    intersect = spread_over_range & wanted_range
    if not intersect:
        return 0
    rate = intersect.days / spread_over_range.days
    return amount * rate

def same_currency(amount1, amount2):
    return not (amount1 and amount2 and amount1.currency != amount2.currency)

def of_currency(amount, currency):
    return not amount or amount.currency == currency
