/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountView.h"
#import "MGConst.h"
#import "MGEntryPrint.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGAccountView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyAccountView *m = [[PyAccountView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"AccountViewView", self)];
    [m release];
    [NSBundle loadNibNamed:@"EntryTable" owner:self];
    entryTable = [[MGEntryTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    filterBar = [[MGFilterBar alloc] initWithPyRef:[[self model] filterBar] view:filterBarView forEntryTable:YES];
    balanceGraph = [[MGBalanceGraph alloc] initWithPyRef:[[self model] balGraph]];
    barGraph = [[MGBarGraph alloc] initWithPyRef:[[self model] barGraph]];
    // We have to put one of the graph in there before we link the prefs
    NSView *graphView = [balanceGraph view];
    [graphView setFrame:[graphPlaceholder frame]];
    [graphView setAutoresizingMask:[graphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:graphPlaceholder with:graphView];
    currentGraphView = [balanceGraph view];
    return self;
}
        
- (void)dealloc
{
    [entryTable release];
    [barGraph release];
    [balanceGraph release];
    [filterBar release];
    [super dealloc];
}

- (PyAccountView *)model
{
    return (PyAccountView *)model;
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : currentGraphView;
    return [[[MGEntryPrint alloc] initWithPyParent:[self model] tableView:tableView
        graphView:printGraphView] autorelease];
}

- (NSString *)tabIconName
{
    return @"entry_table_16";
}

- (void)showGraph:(HSGUIController *)graph
{
    NSView *oldView = currentGraphView;
    NSView *graphView = [graph view];
    [graphView setFrame:[oldView frame]];
    [graphView setAutoresizingMask:[oldView autoresizingMask]];
    [wholeView replaceSubview:oldView with:graphView];
    currentGraphView = [graph view];
}

/* Public */
- (id)fieldEditorForObject:(id)asker
{
    return [entryTable fieldEditorForObject:asker];
}

- (BOOL)canToggleReconciliationMode
{
    return [[self model] canToggleReconciliationMode];
}

- (BOOL)inReconciliationMode
{
    return [[self model] inReconciliationMode];
}

- (void)toggleReconciliationMode
{
    [[self model] toggleReconciliationMode];
}

- (void)toggleReconciled
{
    [[entryTable model] toggleReconciled];
}

/* Actions */
- (IBAction)toggleReconciliationMode:(id)sender
{
    [self toggleReconciliationMode];
}

/* Core --> Cocoa */
- (void)updateVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    BOOL graphVisible = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    // Let's set initial rects
    NSRect mainRect = [tableScrollView frame];
    NSRect graphRect = [[balanceGraph view] frame];
    if (graphVisible) {
        mainRect.size.height = NSMaxY(mainRect) - NSMaxY(graphRect);
        mainRect.origin.y = NSMaxY(graphRect);
    }
    else {
        mainRect.size.height = NSMaxY(mainRect) - NSMinY(graphRect);
        mainRect.origin.y = NSMinY(graphRect);
    }
    [[balanceGraph view] setHidden:!graphVisible];
    [[barGraph view] setHidden:!graphVisible];
    [tableScrollView setFrame:mainRect];
}

- (void)refreshReconciliationButton
{
    if ([self canToggleReconciliationMode]) {
        [reconciliationModeButton setEnabled:YES];
        NSInteger state = [self inReconciliationMode] ? NSOnState : NSOffState;
        [reconciliationModeButton setState:state];
    }
    else {
        [reconciliationModeButton setEnabled:NO];
        [reconciliationModeButton setState:NSOffState];
    }
}

- (void)showLineGraph
{
    [self showGraph:balanceGraph];
}

- (void)showBarGraph
{
    [self showGraph:barGraph];
}
@end