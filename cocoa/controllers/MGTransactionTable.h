#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGTableView.h"
#import "MGDocument.h"
#import "PyTransactionTable.h"
#import "MGEditableTable.h"
#import "MGFilterBar.h"
#import "AMButtonBar.h"
#import "MGFieldEditor.h"

@interface MGTransactionTable : MGEditableTable 
{
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;

    HSTableColumnManager *columnsManager;
    MGFieldEditor *customFieldEditor;
    MGFilterBar *filterBar;
}
- (id)initWithDocument:(MGDocument *)aDocument;

/* Public */

- (PyTransactionTable *)py;
- (id)fieldEditorForObject:(id)asker;

- (void)moveUp;
- (void)moveDown;

@end
