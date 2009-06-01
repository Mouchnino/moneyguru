#import <Cocoa/Cocoa.h>
#import "PyGUI.h"
#import "MGPrintView.h"

@interface MGGUIController : NSObject
{
    PyGUI *py;
}
- (id)initWithPyClassName:(NSString *)aClassName pyParent:(id)aPyParent;
- (NSView *)view;
- (MGPrintView *)viewToPrint;
- (void)connect;
- (void)disconnect;
@end
