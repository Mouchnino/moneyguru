#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyMainWindow : PyGUI {}
- (BOOL)canNavigateDateRange;
- (void)navigateBack;
@end