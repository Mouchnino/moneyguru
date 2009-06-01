#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGDocument.h"
#import "PyEntryTable.h"
#import "MGEditableTable.h"
#import "MGFilterBar.h"
#import "AMButtonBar.h"
#import "MGBalanceGraph.h"
#import "MGBarGraph.h"
#import "MGFieldEditor.h"

@interface MGEntryTable : MGEditableTable 
{   
    IBOutlet NSView *mainView;
    IBOutlet NSView *graphPlaceholder;
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;
    
    HSTableColumnManager *columnsManager;
    MGFieldEditor *customFieldEditor;
    MGFilterBar *filterBar;
    MGBalanceGraph *balanceGraph;
    MGBarGraph *barGraph;
    MGGUIController *currentGraph;
}
- (id)initWithDocument:(MGDocument *)aDocument;

/* Private */
- (void)updateVisibility;

/* Public */
- (PyEntryTable *)py;
- (id)fieldEditorForObject:(id)asker;
- (void)moveUp;
- (void)moveDown;
- (void)showBalanceGraph;
- (void)showBarGraph;
@end
