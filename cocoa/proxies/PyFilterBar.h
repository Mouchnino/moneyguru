#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyFilterBar : PyGUI {}

- (NSString *)filterType;
- (void)setFilterType:(NSString *)filterType;
@end