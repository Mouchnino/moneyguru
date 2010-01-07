/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGTableView.h"
#import "MGDocument.h"
#import "PyTransactionTable.h"
#import "MGEditableTable.h"
#import "MGFilterBar.h"
#import "AMButtonBar.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"

@interface MGTransactionTable : MGEditableTable 
{
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;

    HSTableColumnManager *columnsManager;
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
    MGFilterBar *filterBar;
}
- (id)initWithDocument:(MGDocument *)aDocument;

/* Public */
- (PyTransactionTable *)py;
- (id)fieldEditorForObject:(id)asker;
- (void)showFromAccount:(id)sender;
- (void)showToAccount:(id)sender;
@end
