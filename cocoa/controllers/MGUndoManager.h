#import <Cocoa/Cocoa.h>
#import "PyDocument.h"

@interface MGUndoManager : NSUndoManager
{
    PyDocument *document;
}
- (id)initWithPy:(PyDocument *)aDocument;
@end