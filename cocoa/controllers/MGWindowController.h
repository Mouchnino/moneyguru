#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

// You, it would be nice if objc had multiple inheritance...
// We need the window controllers to be NSWindowController instances if we want the window dealloc
// to be properly made when the document closes.

@interface MGWindowController : NSWindowController
{
    PyGUI *py;
}
- (id)initWithNibName:(NSString *)aNibName pyClassName:(NSString *)aClassName pyParent:(id)aPyParent;
- (void)connect;
- (void)disconnect;
@end
