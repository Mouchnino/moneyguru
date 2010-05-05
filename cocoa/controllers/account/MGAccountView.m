/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGAccountView.h"
#import "MGConst.h"
#import "MGEntryPrint.h"
#import "Utils.h"

@implementation MGAccountView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyAccountView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"EntryTable" owner:self];
    entryTable = [[MGEntryTable alloc] initWithPyParent:[self py] view:tableView];
    filterBar = [[MGFilterBar alloc] initWithPyParent:[self py] view:filterBarView forEntryTable:YES];
    balanceGraph = [[MGBalanceGraph alloc] initWithPyParent:[self py] pyClassName:@"PyBalanceGraph"];
    barGraph = [[MGBarGraph alloc] initWithPyParent:[self py] pyClassName:@"PyBarGraph"];
    // We have to put one of the graph in there before we link the prefs
    NSView *graphView = [balanceGraph view];
    [graphView setFrame:[graphPlaceholder frame]];
    [graphView setAutoresizingMask:[graphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:graphPlaceholder with:graphView];
    currentGraphView = [balanceGraph view];
    
    NSArray *children = [NSArray arrayWithObjects:[entryTable py], [balanceGraph py], [barGraph py],
        [filterBar py], nil];
    [[self py] setChildren:children];
    
    [self updateVisibility];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud addObserver:self forKeyPath:AccountGraphVisible options:NSKeyValueObservingOptionNew context:NULL];
    return self;
}
        
- (void)dealloc
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud removeObserver:self forKeyPath:AccountGraphVisible];
    [entryTable release];
    [barGraph release];
    [balanceGraph release];
    [filterBar release];
    [super dealloc];
}

- (PyAccountView *)py
{
    return (PyAccountView *)py;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGEntryPrint alloc] initWithPyParent:[entryTable py] tableView:tableView
        graphView:currentGraphView] autorelease];
}

/* Private */
- (void)updateVisibility
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    BOOL graphVisible = [ud boolForKey:AccountGraphVisible];
    // Let's set initial rects
    NSRect mainRect = [tableScrollView frame];
    NSRect graphRect = [[balanceGraph view] frame];
    if (graphVisible)
    {
        mainRect.size.height = NSMaxY(mainRect) - NSMaxY(graphRect);
        mainRect.origin.y = NSMaxY(graphRect);
    }
    else
    {
        mainRect.size.height = NSMaxY(mainRect) - NSMinY(graphRect);
        mainRect.origin.y = NSMinY(graphRect);
    }
    [[balanceGraph view] setHidden:!graphVisible];
    [[barGraph view] setHidden:!graphVisible];
    [tableScrollView setFrame:mainRect];
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
    return [[self py] canToggleReconciliationMode];
}

- (BOOL)inReconciliationMode
{
    return [[self py] inReconciliationMode];
}

- (void)toggleReconciliationMode
{
    [[self py] toggleReconciliationMode];
}

- (void)toggleReconciled
{
    [[entryTable py] toggleReconciled];
}

/* Actions */
- (IBAction)toggleReconciliationMode:(id)sender
{
    [self toggleReconciliationMode];
}

/* Delegate */
- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    [self updateVisibility];
}

/* Core --> Cocoa */
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

-(void)refreshTotals
{
    [totalsLabel setStringValue:[py totals]];
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