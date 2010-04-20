/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyAccountView.h"
#import "MGBaseView.h"
#import "MGTableView.h"
#import "AMButtonBar.h"
#import "MGEntryTable.h"
#import "MGFilterBar.h"
#import "MGBalanceGraph.h"
#import "MGBarGraph.h"

@interface MGAccountView : MGBaseView
{
    IBOutlet MGTableView *tableView;
    IBOutlet NSScrollView *tableScrollView;
    IBOutlet NSView *graphPlaceholder;
    IBOutlet AMButtonBar *filterBarView;
    IBOutlet NSTextField *totalsLabel;
    IBOutlet NSButton *reconciliationModeButton;
    
    PyAccountView *py;
    MGEntryTable *entryTable;
    MGFilterBar *filterBar;
    MGBalanceGraph *balanceGraph;
    MGBarGraph *barGraph;
    NSView *currentGraphView;
}
- (id)initWithPyParent:(id)aPyParent;
- (PyAccountView *)py;

/* Private */
- (void)updateVisibility;

/* Public */
- (id)fieldEditorForObject:(id)asker;
- (BOOL)canToggleReconciliationMode;
- (BOOL)inReconciliationMode;
- (void)toggleReconciliationMode;
- (void)toggleReconciled;

/* Actions */
- (IBAction)toggleReconciliationMode:(id)sender;
@end