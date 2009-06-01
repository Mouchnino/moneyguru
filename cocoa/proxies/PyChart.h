#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyChart : PyGUI {}
- (NSArray *)data;
- (NSString *)title;
- (NSString *)currency;
@end