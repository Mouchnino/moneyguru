#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PySearchField : PyGUI {}

- (NSString *)query;
- (void)setQuery:(NSString *)query;
@end