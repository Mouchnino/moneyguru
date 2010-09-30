/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyDateRangeSelector : PyGUI {}
- (void)selectPrevDateRange;
- (void)selectNextDateRange;
- (void)selectTodayDateRange;
- (void)selectMonthRange;
- (void)selectQuarterRange;
- (void)selectYearRange;
- (void)selectYearToDateRange;
- (void)selectRunningYearRange;
- (void)selectAllTransactionsRange;
- (void)selectCustomDateRange;
- (void)selectSavedRange:(NSInteger)slot;
- (NSString *)display;
- (BOOL)canNavigate;
- (NSArray *)customRangeNames;
@end