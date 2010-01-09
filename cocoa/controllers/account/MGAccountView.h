/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGGUIControllerBase.h"
#import "PyAccountView.h"
#import "MGDocument.h"
#import "MGTableView.h"
#import "AMButtonBar.h"
#import "MGEntryTable.h"
#import "MGFilterBar.h"
#import "MGBalanceGraph.h"
#import "MGBarGraph.h"

@interface MGAccountView : MGGUIControllerBase
{
    IBOutlet MGTableView *tableView;
    IBOutlet NSView *wholeView;
    IBOutlet NSView *mainView;
    IBOutlet NSView *graphPlaceholder;
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;
    
    PyAccountView *py;
    MGEntryTable *entryTable;
    MGFilterBar *filterBar;
    MGBalanceGraph *balanceGraph;
    MGBarGraph *barGraph;
    NSView *currentGraphView;
}
- (id)initWithDocument:(MGDocument *)aDocument;

/* Private */
- (void)updateVisibility;

- (PyAccountView *)py;
// Temporary
- (MGEntryTable *)entryTable;
@end