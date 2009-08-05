/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
