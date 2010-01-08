/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGAccountView.h"
#import "MGConst.h"
#import "MGEntryPrint.h"

@implementation MGAccountView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"EntryTable" owner:self];
    entryTable = [[MGEntryTable alloc] initWithDocument:aDocument view:tableView totalsLabel:totalsLabel];
    filterBar = [[MGFilterBar alloc] initWithDocument:aDocument view:filterBarView forEntryTable:YES];
    balanceGraph = [[MGBalanceGraph alloc] initWithDocument:aDocument pyClassName:@"PyBalanceGraph"];
    barGraph = [[MGBarGraph alloc] initWithDocument:aDocument pyClassName:@"PyBarGraph"];
    // We have to put one of the graph in there before we link the prefs
    NSView *graphView = [balanceGraph view];
    [graphView setFrame:[graphPlaceholder frame]];
    [graphView setAutoresizingMask:[graphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:graphPlaceholder with:graphView];
    currentGraph = balanceGraph;
    
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

- (NSView *)view
{
    return wholeView;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGEntryPrint alloc] initWithPyParent:[entryTable py] tableView:tableView
        graphView:[currentGraph view]] autorelease];
}

- (void)connect
{
    [entryTable connect];
    [filterBar connect];
    if (currentGraph != nil)
        [currentGraph connect];
}

- (void)disconnect
{
    [entryTable disconnect];
    [filterBar disconnect];
    if (currentGraph != nil)
        [currentGraph disconnect];
}

- (MGEntryTable *)entryTable
{
    return entryTable;
}

/* Private */
- (void)updateVisibility
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    BOOL graphVisible = [ud boolForKey:AccountGraphVisible];
    // Let's set initial rects
    NSRect mainRect = [mainView frame];
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
    [mainView setFrame:mainRect];
}

- (void)showGraph:(MGGUIController *)graph
{
    NSView *oldView = [currentGraph view];
    [currentGraph disconnect];
    NSView *graphView = [graph view];
    [graphView setFrame:[oldView frame]];
    [graphView setAutoresizingMask:[oldView autoresizingMask]];
    [wholeView replaceSubview:oldView with:graphView];
    [graph connect];
    currentGraph = graph;
}

/* Public */
- (void)showBalanceGraph
{
    [self showGraph:balanceGraph];
}

- (void)showBarGraph
{
    [self showGraph:barGraph];
}

/* Delegate */
- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    [self updateVisibility];
}
@end