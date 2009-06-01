#import <Cocoa/Cocoa.h>
#import "MGGUIController.h"
#import "MGDocument.h"
#import "PySearchField.h"

@interface MGSearchField : MGGUIController
{   
    IBOutlet NSSearchField *view;
}
- (id)initWithDocument:(MGDocument *)aDocument;

- (PySearchField *)py;
- (IBAction)changeQuery:(id)sender;
@end