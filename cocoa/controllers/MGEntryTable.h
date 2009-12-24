/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
#import "MGDateFieldEditor.h"

@interface MGEntryTable : MGEditableTable 
{   
    IBOutlet NSView *mainView;
    IBOutlet NSView *graphPlaceholder;
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;
    
    HSTableColumnManager *columnsManager;
    MGFieldEditor *customFieldEditor;
    MGDateFieldEditor *customDateFieldEditor;
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
- (void)showBalanceGraph;
- (void)showBarGraph;
@end
