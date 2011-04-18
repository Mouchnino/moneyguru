/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyPanel.h"

@interface PyCustomDateRangePanel : PyPanel {}
- (NSString *)startDate;
- (void)setStartDate:(NSString *)date;
- (NSString *)endDate;
- (void)setEndDate:(NSString *)date;
- (NSInteger)slotIndex;
- (void)setSlotIndex:(NSInteger)index;
- (NSString *)slotName;
- (void)setSlotName:(NSString *)name;
@end