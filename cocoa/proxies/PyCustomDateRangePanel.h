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