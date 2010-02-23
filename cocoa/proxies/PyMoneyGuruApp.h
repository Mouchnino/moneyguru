/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyRegistrable.h"

@interface PyMoneyGuruApp : PyRegistrable {}

- (id)initWithCocoa:(id)cocoa;
- (void)free;

/* Preferences */
- (NSInteger)firstWeekday; // 0 = monday, 6 = sunday
- (void)setFirstWeekday:(NSInteger)weekday;
- (NSInteger)aheadMonths;
- (void)setAheadMonths:(NSInteger)months;
- (NSInteger)yearStartMonth; // 0 = Jan 11 = Dec
- (void)setYearStartMonth:(NSInteger)month;
- (NSInteger)autoSaveInterval;
- (void)setAutoSaveInterval:(NSInteger)minutes;
- (BOOL)autoDecimalPlace;
- (void)setAutoDecimalPlace:(BOOL)value;
@end