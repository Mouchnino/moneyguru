# Created By: Virgil Dupras
# Created On: 2008-06-18
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_
from hsutil.testcase import TestCase

from ...gui.date_widget import DateWidget, DAY, MONTH, YEAR

class Pristine(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
    
    def test_date(self):
        """Default date is today"""
        self.assertEqual(self.w.date, date.today())
    
    def test_set_text(self):
        # It's possible to set the text to set the internal date
        self.w.text = '12/08/2009'
        eq_(self.w.date, date(2009, 8, 12))
    

class DDMMYYYYWithSlash(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
    
    def _assert_unchanged(self):
        self.assertEqual(self.w.text, '12/06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 12))
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_backspace(self):
        """When not buffering, it does nothing"""
        self.w.backspace()
        self._assert_unchanged()
    
    def test_date(self):
        """The date has been correctly set"""
        self.assertEqual(self.w.date, date(2008, 6, 12))
    
    def test_decrease(self):
        """decrease() decreases the day by one"""
        self.w.decrease()
        self.assertEqual(self.w.date, date(2008, 6, 11))
    
    def test_increase(self):
        """increase() increases the day by one"""
        self.w.increase()
        self.assertEqual(self.w.date, date(2008, 6, 13))
    
    def test_left(self):
        """Going left selects the year"""
        self.w.left()
        self.assertEqual(self.w.selection, (6, 9))
    
    def test_left_rollover(self):
        """Make sur that rollover happens instead of indexes going in the negative (don't crash at
        the second rollover)"""
        self.w.left() # first rollover
        self.w.left() 
        self.w.left() # Day again
        self.w.left() # second rollover
        self.assertEqual(self.w.selection, (6, 9))
    
    def test_right(self):
        """Going right selects the month"""
        self.w.right()
        self.assertEqual(self.w.selection, (3, 4))
    
    def test_selection(self):
        """The day field is selected"""
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_text(self):
        """Text is the formatted date"""
        self.assertEqual(self.w.text, '12/06/2008')
    
    def test_type_0(self):
        """Typing 0 enters in buffering mode"""
        self.w.type('0')
        self.assertEqual(self.w.text, '0 /06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 12)) # date hasn't changed yet
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_type_31(self):
        """Even if the current date is in a non-31 month, it's still possible to type '31' in the 
        day field.
        """
        self.w.type('3')
        self.w.type('1')
        self.assertEqual(self.w.text, '31/06/2008') # yup, that's strange, but it's what we want
        self.assertEqual(self.w.date, date(2008, 6, 30))
        self.w.exit() # When exiting the field, the date *must* fix itself
        self.assertEqual(self.w.text, '30/06/2008')
    
    def test_type_31_then_exit(self):
        """When exiting the first, the text of the widget must be a *corrected* date"""
        self.w.type('3')
        self.w.type('1')
        self.w.exit() # When exiting the field, the date *must* fix itself
        self.assertEqual(self.w.text, '30/06/2008')
    
    def test_type_4(self):
        """Typing 4 also enters buffering mode even though it's not possible to type another digit"""
        self.w.type('4')
        self.assertEqual(self.w.text, '4 /06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 12)) # date hasn't changed yet
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_type_garbage(self):
        """Ignore any typing that is not either a digit or the separator"""
        self.w.type(' ')
        self.w.type('a')
        self.w.type('b')
        self.w.type('!')
        self._assert_unchanged()
    
    def test_type_slash(self):
        """Typing the separator doesn't do anything because we're not buffering"""
        self.w.type('/')
        self._assert_unchanged()
    

class DDMMYYYYWithSlashMonthSelected(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.right()
    
    def test_decrease(self):
        """decrease() decreases the month by one"""
        self.w.decrease()
        self.assertEqual(self.w.date, date(2008, 5, 12))
    
    def test_increase(self):
        """increase() increases the month by one"""
        self.w.increase()
        self.assertEqual(self.w.date, date(2008, 7, 12))
    
    def test_left(self):
        """Going left selects the day"""
        self.w.left()
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_right(self):
        """Going right selects the year"""
        self.w.right()
        self.assertEqual(self.w.selection, (6, 9))
    
    def test_type_0(self):
        """Typing 0 enters in buffering mode"""
        self.w.type('0')
        self.assertEqual(self.w.text, '12/0 /2008')
        self.assertEqual(self.w.date, date(2008, 6, 12)) # date hasn't changed yet
        self.assertEqual(self.w.selection, (3, 4))
    
    def test_type_2(self):
        """Typing 2 also enters buffering mode even though it's not possible to type another digit"""
        self.w.type('2')
        self.assertEqual(self.w.text, '12/2 /2008')
        self.assertEqual(self.w.date, date(2008, 6, 12)) # date hasn't changed yet
        self.assertEqual(self.w.selection, (3, 4))
    

class DDMMYYYYWithSlashYearSelected(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.left()
    
    def test_decrease(self):
        """decrease() decreases the month by one"""
        self.w.decrease()
        self.assertEqual(self.w.date, date(2007, 6, 12))
    
    def test_increase(self):
        """increase() increases the month by one"""
        self.w.increase()
        self.assertEqual(self.w.date, date(2009, 6, 12))
    
    def test_left(self):
        """Going left selects the month"""
        self.w.left()
        self.assertEqual(self.w.selection, (3, 4))
    
    def test_right(self):
        """Going right selects the day"""
        self.w.right()
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_type_2(self):
        """Typing 2 enters in buffering mode"""
        self.w.type('2')
        self.assertEqual(self.w.text, '12/06/2   ')
        self.assertEqual(self.w.date, date(2008, 6, 12)) # date hasn't changed yet
        self.assertEqual(self.w.selection, (6, 9))
    
    def test_type69slash(self):
        """A 2-digits year >= 69 ends up as a 1900's year. The selected field is still the year"""
        self.w.type('6')
        self.w.type('9')
        self.w.type('/')
        self.assertEqual(self.w.text, '12/06/1969')
        self.assertEqual(self.w.date, date(1969, 6, 12))
        self.assertEqual(self.w.selection, (6, 9))
    

class DDMMYYYYWithSlashBuffering(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.type('1')
    
    def test_backspace(self):
        """Removes the only buffered char and thus cancels buffering"""
        self.w.backspace()
        self.assertEqual(self.w.text, '12/06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 12))
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_decrease(self):
        """Flush the buffer then decrease the new value"""
        self.w.decrease()
        self.assertEqual(self.w.date, date(2008, 5, 31))
    
    def test_increase(self):
        """Flush the buffer then increase the new value"""
        self.w.increase()
        self.assertEqual(self.w.date, date(2008, 6, 2))
    
    def test_left(self):
        """Flush the buffer then go left"""
        self.w.left()
        self.assertEqual(self.w.selection, (6, 9))
        self.assertEqual(self.w.date, date(2008, 6, 1))
    
    def test_right(self):
        """Flush the buffer then go left"""
        self.w.right()
        self.assertEqual(self.w.selection, (3, 4))
        self.assertEqual(self.w.date, date(2008, 6, 1))
    
    def test_type_4(self):
        """Typing 4 completes the buffer and goes to the month field"""
        self.w.type('4')
        self.assertEqual(self.w.text, '14/06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 14))
        self.assertEqual(self.w.selection, (3, 4))
    
    def test_type_slash(self):
        """Typing the separator saves the bufferand goes to the month field"""
        self.w.type('/')
        self.assertEqual(self.w.text, '01/06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 1))
        self.assertEqual(self.w.selection, (3, 4))
    

class DDMMYYYYWithSlashBufferingZero(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.type('0')
    
    def test_type_1(self):
        """Typing 1 completes the buffer and goes to the month field"""
        # Previously, it would stay in the day field because the int value is < than 4, the limit
        # for the first digit to invalidate the possibility of a second digit
        self.w.type('1')
        self.assertEqual(self.w.text, '01/06/2008')
        self.assertEqual(self.w.date, date(2008, 6, 1))
        self.assertEqual(self.w.selection, (3, 4))
    

class DDMMYYYYWithSlashMonthSelectedBuffering(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.right()
        self.w.type('1')
    
    def test_exit(self):
        """Flushes the buffer and return the focus to day"""
        self.w.exit()
        self.assertEqual(self.w.text, '12/01/2008')
        self.assertEqual(self.w.date, date(2008, 1, 12))
        self.assertEqual(self.w.selection, (0, 1))
    
    def test_type_3(self):
        """Typing 3 (resulting in an invalid month) does nothing"""
        self.w.type('3')
        self.assertEqual(self.w.text, '12/1 /2008')
        self.assertEqual(self.w.date, date(2008, 6, 12))
        self.assertEqual(self.w.selection, (3, 4))
    

class DDMMYYYYWithSlashYearSelectedBuffering(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.left()
        self.w.type('2')
    
    def test_type_0(self):
        """With the year, there is no premature end of edition"""
        self.w.type('0')
        self.assertEqual(self.w.text, '12/06/20  ')
        self.assertEqual(self.w.date, date(2008, 6, 12)) # date hasn't changed yet
        self.assertEqual(self.w.selection, (6, 9))
    

class DDMMYYYYWithSlashYearSelectedDoubleBuffering(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.left()
        self.w.type('2')
        self.w.type('0')
    
    def test_backspace(self):
        """backspace with 2 chars in the buffer doesn't cancel buffering, it just removes the last char"""
        self.w.backspace()
        self.assertEqual(self.w.text, '12/06/2   ')
    
    def test_type_07(self):
        """We end up flushing the year after 4 characters"""
        self.w.type('0')
        self.w.type('7')
        self.assertEqual(self.w.text, '12/06/2007')
        self.assertEqual(self.w.date, date(2007, 6, 12))
        self.assertEqual(self.w.selection, (6, 9)) # We stay on the year field
    
    def test_type_splash(self):
        """It's possible to flush a 2-length year"""
        self.w.type('/')
        self.assertEqual(self.w.text, '12/06/2020')
        self.assertEqual(self.w.date, date(2020, 6, 12))
        self.assertEqual(self.w.selection, (6, 9))
    

class DDMMYYYYWithHyphen(TestCase):
    def setUp(self):
        self.w = DateWidget('dd-MM-yyyy')
        self.w.date = date(2008, 6, 12)
    
    def test_text(self):
        """Text is the formatted date"""
        self.assertEqual(self.w.text, '12-06-2008')
    
    def test_type_1hypen(self):
        """Hyphen being the separator, typing it flushes the buffer and moves next"""
        self.w.type('2')
        self.w.type('-')
        self.assertEqual(self.w.text, '02-06-2008')
    

class YYYYMMDDWithDot(TestCase):
    def setUp(self):
        self.w = DateWidget('yyyy.MM.dd')
        self.w.date = date(2008, 6, 12)
    
    def test_left(self):
        """Selects the month which is in the middle"""
        self.w.left()
        self.assertEqual(self.w.selection, (5, 6))
    
    def test_right(self):
        """Selects the year which is first"""
        self.w.right()
        self.assertEqual(self.w.selection, (0, 3))
    
    def test_selection(self):
        """The day is selected, which is in last position"""
        self.assertEqual(self.w.selection, (8, 9))
    
    def test_text(self):
        """Text is the formatted date"""
        self.assertEqual(self.w.text, '2008.06.12')
    

class DDMMYYYYOnJanuaryFocusOnMonth(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 1, 12)
        self.w.right()
    
    def test_decrease(self):
        """A rollover happens and the year decrements"""
        self.w.decrease()
        self.assertEqual(self.w.date, date(2007, 12, 12))
    

class DDMMYYYYOnDecemberFocusOnMonth(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 12, 12)
        self.w.right()
    
    def test_increase(self):
        """A rollover happens and the year increments"""
        self.w.increase()
        self.assertEqual(self.w.date, date(2009, 1, 12))
    
class DDMMYYYYOnLastDayOfJanuary(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 1, 31)
    
    def test_increase_month(self):
        # don't crash, adjust the day
        self.w.right()
        self.w.increase()
        self.assertEqual(self.w.date, date(2008, 2, 29))
    

class DDMMYYYYOnLastDayOfMarch(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 3, 31)
    
    def test_decrease_month(self):
        # don't crash, adjust the day
        self.w.right()
        self.w.decrease()
        self.assertEqual(self.w.date, date(2008, 2, 29))
    

class DDMMYY(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yy')
        self.w.date = date(2008, 11, 12)
    
    def test_text(self):
        """Year is shown in a 2 digits fashion"""
        self.assertEqual(self.w.text, '12/11/08')
    

class DMYY(TestCase):
    def setUp(self):
        self.w = DateWidget('d/M/yy')
        self.w.date = date(2008, 1, 2)
    
    def test_selection(self):
        """Selection is only 1 in length"""
        self.assertEqual(self.w.selection, (0, 0))
    
    def test_text(self):
        """Year is shown in a 2 digits fashion"""
        self.assertEqual(self.w.text, '2/1/08')
    
    def test_type_1(self):
        """Always buffer at least 1 character at all time"""
        self.w.type('1')
        self.assertEqual(self.w.text, '1 /1/08')
        self.assertEqual(self.w.selection, (0, 1))
    

class DMYYWideMonth(TestCase):
    def setUp(self):
        self.w = DateWidget('d/M/yy')
        self.w.date = date(2008, 11, 2)
    
    def test_right(self):
        """The month's selection is also 2 in length"""
        self.w.right()
        self.assertEqual(self.w.selection, (2, 3))
    
    def test_selection(self):
        """When the element is 2 in length, the selection's length is also 2"""
        self.assertEqual(self.w.selection, (0, 0))
    
    def test_text(self):
        """Year is shown in a 2 digits fashion"""
        self.assertEqual(self.w.text, '2/11/08')
    

class SetInvalidDate(TestCase):
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.text = '--'
    
    def test_date(self):
        # the 'date' attribute returns None when invalid
        assert self.w.date is None
    
    def test_displayed_text(self):
        # When the date is invalid, display '-' chars in the current format
        eq_(self.w.text, '--/--/----')
    
    def test_increase_decrease(self):
        # Trying to increase/decrease an invalid date doesn't do anything, but it doesn't crash either
        self.w.increase() # no crash
        self.w.decrease() # no crash
        eq_(self.w.text, '--/--/----')
        
    
    def test_type_1(self):
        # When we start typing, the rest of the "-" chars stay there
        self.w.type('1')
        eq_(self.w.text, '1 /--/----')
    

class InvalidBuffer(TestCase):
    # The widget is currently in buffer mode, but with a "0" (invalid) in its buffer
    def setUp(self):
        self.w = DateWidget('dd/MM/yyyy')
        self.w.date = date(2008, 6, 12)
        self.w.type('0')
    
    def test_exit(self):
        # exiting cancels the buffer if invalid
        self.w.exit()
        self.assertEqual(self.w.text, '12/06/2008')
    
    def test_left(self):
        # going left cancels the buffer if invalid
        self.w.left()
        self.assertEqual(self.w.text, '12/06/2008')
    
    def test_increase(self):
        # When increasing, cancel the buffer if it's invalid
        self.w.increase()
        self.assertEqual(self.w.text, '13/06/2008')
    
    def test_right(self):
        # going left cancels the buffer if invalid
        self.w.right()
        self.assertEqual(self.w.text, '12/06/2008')
    
    def test_type_sep(self):
        # There was a crash when a sep-caused _flush_buffer would be called with an invalid value
        self.w.type('/')
        self.assertEqual(self.w.text, '0 /06/2008') # don't do anything (stay on DAY)
    
