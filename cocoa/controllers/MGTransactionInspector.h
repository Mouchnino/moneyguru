/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGSplitTable.h"
#import "MGWindowController.h"
#import "PyTransactionPanel.h"

@interface MGTransactionInspector : MGPanel {
    IBOutlet MGTextField *dateField;
    IBOutlet MGTextField *descriptionField;
    IBOutlet MGTextField *payeeField;
    IBOutlet MGTextField *checknoField;
    IBOutlet MGSplitTable *splitTable;
    IBOutlet NSButton *mctBalanceButton;
    
    NSTextView *customFieldEditor;
    NSTextView *customDateFieldEditor;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyTransactionPanel *)py;
/* Actions */
- (IBAction)mctBalance:(id)sender;
@end
