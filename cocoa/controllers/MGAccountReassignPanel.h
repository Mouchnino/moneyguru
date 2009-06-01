#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGWindowController.h"
#import "PyAccountReassignPanel.h"

@interface MGAccountReassignPanel : MGWindowController {
    IBOutlet NSPopUpButton *accountSelector;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyAccountReassignPanel *)py;
/* Public */
- (void)load;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)ok:(id)sender;
@end