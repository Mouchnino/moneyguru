/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

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
- (int)firstWeekday; // 0 = monday, 6 = sunday
- (void)setFirstWeekday:(int)weekday;
- (int)aheadMonths;
- (void)setAheadMonths:(int)months;
- (BOOL)dontUnreconcile;
- (void)setDontUnreconcile:(BOOL)flag;
@end