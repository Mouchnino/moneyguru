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
    self = [super init];
    [NSBundle loadNibNamed:@"EntryTable" owner:self];
    entryTable = [[MGEntryTable alloc] initWithPyParent:aPyParent view:tableView];
    filterBar = [[MGFilterBar alloc] initWithPyParent:aPyParent view:filterBarView forEntryTable:YES];
    balanceGraph = [[MGBalanceGraph alloc] initWithPyParent:aPyParent pyClassName:@"PyBalanceGraph"];
    barGraph = [[MGBarGraph alloc] initWithPyParent:aPyParent pyClassName:@"PyBarGraph"];
    // We have to put one of the graph in there before we link the prefs
    NSView *graphView = [balanceGraph view];
    [graphView setFrame:[graphPlaceholder frame]];
    [graphView setAutoresizingMask:[graphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:graphPlaceholder with:graphView];
    currentGraphView = [balanceGraph view];
    
    NSArray *children = [NSArray arrayWithObjects:[entryTable py], [balanceGraph py], [barGraph py],
        [filterBar py], nil];
    Class pyClass = [Utils classNamed:@"PyAccountView"];
    py = [[pyClass alloc] initWithCocoa:self pyParent:aPyParent children:children];
    
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
    [py release];
    [super dealloc];
}

- (oneway void)release
{
    if ([self retainCount] == 2)
        [py free];
    [super release];
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

- (void)toggleReconciled
{
    [[entryTable py] toggleReconciled];
}

/* Delegate */
- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    [self updateVisibility];
}

/* Core --> Cocoa */
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