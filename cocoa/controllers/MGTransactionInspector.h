#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGSplitTable.h"
#import "MGWindowController.h"
#import "PyTransactionPanel.h"

@interface MGTransactionInspector : MGWindowController {
    IBOutlet MGTextField *dateField;
    IBOutlet MGTextField *descriptionField;
    IBOutlet MGTextField *payeeField;
    IBOutlet MGTextField *checknoField;
    IBOutlet MGSplitTable *splitTable;
    IBOutlet NSPopUpButton *repeatOptionsPopUp;
    IBOutlet NSButton *mctBalanceButton;
    
    NSTextView *customFieldEditor;
    NSTextView *customDateFieldEditor;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyTransactionPanel *)py;
/* Methods */
- (BOOL)canLoad;
- (void)load;
- (void)save;
/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)mctBalance:(id)sender;
- (IBAction)save:(id)sender;
@end
