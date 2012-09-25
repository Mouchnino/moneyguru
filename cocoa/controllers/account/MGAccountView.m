/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountView.h"
#import "MGAccountView_UI.h"
#import "MGConst.h"
#import "MGEntryPrint.h"
#import "HSPyUtil.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGAccountView

@synthesize splitView;
@synthesize tableView;
@synthesize filterBarView;
@synthesize reconciliationModeButton;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyAccountView *m = [[PyAccountView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    self.view = createMGAccountView_UI(self);
    entryTable = [[MGEntryTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    filterBar = [[MGFilterBar alloc] initWithPyRef:[[self model] filterBar] view:filterBarView forEntryTable:YES];
    balanceGraph = [[MGBalanceGraph alloc] initWithPyRef:[[self model] balGraph]];
    barGraph = [[MGBarGraph alloc] initWithPyRef:[[self model] barGraph]];
    [m bindCallback:createCallback(@"AccountViewView", self)];
    [m release];
    [splitView setDelegate:self];
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

/* Overrides */
- (PyAccountView *)model
{
    return (PyAccountView *)model;
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : graphView;
    return [[[MGEntryPrint alloc] initWithPyParent:[self model] tableView:tableView
        graphView:printGraphView] autorelease];
}

- (NSString *)tabIconName
{
    return @"entry_table_16";
}

- (void)applySubviewsSizeRestoration
{
    if ([self.model graphHeightToRestore] > 0) {
        [splitView setPosition:NSHeight([splitView frame])-[self.model graphHeightToRestore] ofDividerAtIndex:0];
    }
}

/* Private */
- (void)showGraph:(HSGUIController *)graph
{
    graphView = [graph view];
    [graphView setFrame:NSMakeRect(0, 0, 1, 258)];
    [splitView addSubview:graphView];
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

/* Delegate */
- (CGFloat)splitView:(NSSplitView *)aSplitView constrainMinCoordinate:(CGFloat)proposedMin ofSubviewAt:(NSInteger)dividerIndex
{
    if (aSplitView == splitView) {
        return 200;
    }
    return proposedMin;
}

- (CGFloat)splitView:(NSSplitView *)aSplitView constrainMaxCoordinate:(CGFloat)proposedMax ofSubviewAt:(NSInteger)dividerIndex
{
    if (aSplitView == splitView) {
        return NSHeight([splitView frame]) - 130;
    }
    return proposedMax;
}

- (BOOL)splitView:(NSSplitView *)aSplitView canCollapseSubview:(NSView *)subview
{
    if (subview == graphView) {
        return graphCollapsed;
    }
    return NO;
}

/* Core --> Cocoa */
- (void)updateVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    BOOL graphVisible = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    if (graphVisible) {
        if (graphCollapsed) {
            graphCollapsed = NO;
            CGFloat pos = NSHeight([splitView frame]) - graphCollapseHeight - [splitView dividerThickness];
            [splitView setPosition:pos ofDividerAtIndex:0];
        }
    }
    else {
        if (!graphCollapsed) {
            graphCollapsed = YES;
            graphCollapseHeight = NSHeight([graphView frame]);
            [splitView setPosition:NSHeight([splitView frame]) ofDividerAtIndex:0];
        }
    }
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