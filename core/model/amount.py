# Created By: Eric Mc Sween
# Created On: 2007-12-13
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from itertools import groupby

from hscommon.currency import Currency

try:
    from ._amount import Amount
except ImportError:
    print("Using amount_ref")
    from ._amount_ref import Amount

re_arithmetic_operators = re.compile(r"[+\-*/()]")
re_not_arithmetic_operators = re.compile(r"[^+\-*/()]+")
# 3 letters (capturing)
re_currency = re.compile(r'([a-zA-Z]{3}\s*$)|(^\s*[a-zA-Z]{3})')
# grouping separator. A thousand sep character that has digit before and after *if* the right part
# has 3 digits. \xa0 is a non-breaking space. We sometimes end up with those in space-separated
# environments.
re_grouping_sep = re.compile(r"(?<=\d)[.\s\xA0,'](?=\d{3})")
# A dot or comma followed by digits followed by the end of the string.
# currencies with 2 decimal places
re_decimal_sep_2 = re.compile(r"[,.](?=\d{1,2}$)")
# currencies with 3 or more decimal places
re_decimal_sep_x = re.compile(r"[,.](?=\d{1,10}$)")
# A valid amount, once it has been pre-processed
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

def parse_amount_expression(string, exponent):
    # Parse an expression. Before we can do that, we need to replace all amounts with their parsed
    # and then reformatted counterparts.
    def repl(match):
        s = match.group(0).strip()
        if not s:
            return None
        parsed = parse_amount_single(s, exponent, auto_decimal_place=False)
        fmt = '{{:1.{}f}}'.format(exponent)
        return fmt.format(parsed)
    
    result = re_not_arithmetic_operators.sub(repl, string)
    return result

def parse_amount_single(string, exponent, auto_decimal_place):
    # Parse a string which contains a single amount (not an expression) and return a float
    # Now, we have a string that might have thousand separators and might or might not have
    # a decimal separator, which might be either "," or ".". We'll first find our decimal sep
    # and replace it with a placeholder char, find all thousand seps, replace them with nothing.
    if exponent >= 3:
        string = re_decimal_sep_x.sub('|', string)
    elif exponent == 2:
        string = re_decimal_sep_2.sub('|', string)
    else:
        pass # No decimal sep
    string = re_grouping_sep.sub('', string)
    string = string.replace('|', '.')
    if auto_decimal_place and string.isdigit():
        if exponent:
            string = string.rjust(exponent, '0')
            string = string[:-exponent] + '.' + string[-exponent:]
    try:
        value = float(string)
    except ValueError:
        # There might be some crap around the amount. Remove it and try again.
        m = re_amount.search(string)
        if m is None:
            raise ValueError("'{}' is not an amount".format(string))
        value = float(string[m.start():m.end()])
        if '-' in string[:m.start()]:
            value = -value
    return value

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
    exponent = currency.exponent if currency is not None else 2
    string = string.strip()
    # When we have an expression, we deal only with "simple" numbers. Turning expression off when
    # there's no sign of arithmetic operators allow for complex number parsing so that we can
    # correctly parse thousand separators.
    if with_expression and re_arithmetic_operators.search(string) is None:
        with_expression = False
    if with_expression:
        string = parse_amount_expression(string, exponent)
        try:
            value = eval(string)
        except (SyntaxError, ZeroDivisionError):
            raise ValueError('Invalid expression %r' % string)
        if not isinstance(value, (float, int)):
            raise ValueError('Invalid expression %r' % string)
    else:
        value = parse_amount_single(string, exponent, auto_decimal_place)
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
