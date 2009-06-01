#import <Cocoa/Cocoa.h>
#import "MGGUIController.h"
#import "MGDocument.h"
#import "AMButtonBar.h"
#import "PyFilterBar.h"
#import "PyEntryFilterBar.h"

@interface MGFilterBar : MGGUIController
{   
    AMButtonBar *view;
}
- (id)initWithDocument:(MGDocument *)aDocument view:(AMButtonBar *)view forEntryTable:(BOOL)forEntryTable;
- (PyFilterBar *)py;
@end