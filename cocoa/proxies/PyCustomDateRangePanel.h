/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyCustomDateRangePanel : PyGUI {}
- (void)loadPanel;
- (void)ok;
- (NSString *)startDate;
- (void)setStartDate:(NSString *)date;
- (NSString *)endDate;
- (void)setEndDate:(NSString *)date;
@end