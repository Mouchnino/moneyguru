#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGWindowController.h"
#import "PyCustomDateRangePanel.h"

@interface MGCustomDateRangePanel : MGWindowController {
    IBOutlet MGTextField *startDateField;
    IBOutlet MGTextField *endDateField;
    
    NSTextView *customDateFieldEditor;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyCustomDateRangePanel *)py;
/* Public */
- (void)load;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)ok:(id)sender;
@end