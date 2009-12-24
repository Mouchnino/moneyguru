/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGEntryTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGTableView.h"
#import "MGReconciliationCell.h"
#import "MGEntryPrint.h"

@implementation MGEntryTable

- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyEntryTable" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"EntryTable" owner:self];
    [tableView registerForDraggedTypes:[NSArray arrayWithObject:MGEntryPasteboardType]];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:tableView];
    [columnsManager linkColumn:@"description" toUserDefault:AccountDescriptionColumnVisible];
    [columnsManager linkColumn:@"payee" toUserDefault:AccountPayeeColumnVisible];
    [columnsManager linkColumn:@"checkno" toUserDefault:AccountChecknoColumnVisible];
    customFieldEditor = [[MGFieldEditor alloc] init];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    filterBar = [[MGFilterBar alloc] initWithDocument:aDocument view:filterBarView forEntryTable:YES];
    balanceGraph = [[MGBalanceGraph alloc] initWithDocument:aDocument pyClassName:@"PyBalanceGraph"];
    barGraph = [[MGBarGraph alloc] initWithDocument:aDocument pyClassName:@"PyBarGraph"];
    // We have to put one of the graph in there before e link the prefs
    NSView *graphView = [balanceGraph view];
    [graphView setFrame:[graphPlaceholder frame]];
    [graphView setAutoresizingMask:[graphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:graphPlaceholder with:graphView];
    currentGraph = balanceGraph;
    
    [self updateVisibility];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud addObserver:self forKeyPath:AccountGraphVisible options:NSKeyValueObservingOptionNew context:NULL];
    [self changeColumns]; // initial set
    return self;
}
        
- (void)dealloc
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud removeObserver:self forKeyPath:AccountGraphVisible];
    [barGraph release];
    [balanceGraph release];
    [filterBar release];
    [customFieldEditor release];
    [columnsManager release];
    [super dealloc];
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

/* Override */

- (PyEntryTable *)py
{
    return (PyEntryTable *)py;
}

- (void)connect
{
    [super connect];
    [filterBar connect];
    if (currentGraph != nil)
        [currentGraph connect];
}

- (void)disconnect
{
    [super disconnect];
    [filterBar disconnect];
    if (currentGraph != nil)
        [currentGraph disconnect];
}

- (NSView *)viewToPrint
{
    return [[[MGEntryPrint alloc] initWithPyParent:py tableView:[self tableView] 
        graphView:[currentGraph view]] autorelease];
}

/* Data source */

- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:MGEntryPasteboardType] owner:self];
    [pboard setData:data forType:MGEntryPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(int)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropAbove)
    {
        NSPasteboard* pboard = [info draggingPasteboard];
        NSData* rowData = [pboard dataForType:MGEntryPasteboardType];
        NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
        if ([[self py] canMoveRows:[Utils indexSet2Array:rowIndexes] to:row])
        {
            return NSDragOperationMove;
        }
    }
    return NSDragOperationNone;
}

- (BOOL)tableView:(NSTableView *)aTableView acceptDrop:(id <NSDraggingInfo>)info
              row:(int)row dropOperation:(NSTableViewDropOperation)operation
{
    NSPasteboard* pboard = [info draggingPasteboard];
    NSData* rowData = [pboard dataForType:MGEntryPasteboardType];
    NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    [[self py] moveRows:[Utils indexSet2Array:rowIndexes] to:row];
    return YES;
}

- (id)tableView:(NSTableView *)aTableView objectValueForTableColumn:(NSTableColumn *)column row:(int)row
{
    if ([[column identifier] isEqualToString:@"status"])
    {
        return nil; // special column
    }
    return [super tableView:aTableView objectValueForTableColumn:column row:row];
}

- (void)tableView:(NSTableView *)aTableView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column row:(int)row
{
    if ([[column identifier] isEqualToString:@"status"])
    {
        if ([[self py] canReconcileEntryAtRow:row])
        {
            [[self py] toggleReconciledAtRow:row];
        }
        return;
    }
    [super tableView:aTableView setObjectValue:value forTableColumn:column row:row];
}

/* Delegate */

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)column row:(int)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows])
    {
        return;
    }
    if ([[column identifier] isEqualToString:@"balance"])
    {
        NSColor *color = [[self py] isBalanceNegativeAtRow:row] ? [NSColor redColor] : [NSColor blackColor];
        [cell setTextColor:color];
    }
    else if ([[column identifier] isEqualToString:@"status"])
    {
        MGReconciliationCell *rcell = cell;
        if (row == [tableView editedRow])
        {
            [rcell setIsInFuture:[[self py] isEditedRowInTheFuture]];
            [rcell setIsInPast:[[self py] isEditedRowInThePast]];
        }
        else
        {
            [rcell setIsInFuture:NO];
            [rcell setIsInPast:NO];
        }
        [rcell setCanReconcile:[[self py] canReconcileEntryAtRow:row]];
        [rcell setReconciled:n2b([[self py] valueForColumn:@"reconciled" row:row])];
        [rcell setReconciliationPending:n2b([[self py] valueForColumn:@"reconciliation_pending" row:row])];
        [rcell setRecurrent:n2b([[self py] valueForColumn:@"recurrent" row:row])];
        [rcell setIsBudget:n2b([[self py] valueForColumn:@"is_budget" row:row])];
    }
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self py] toggleReconciled];
    return YES;
}

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    [self updateVisibility];
}

/* Public */

- (id)fieldEditorForObject:(id)asker
{
    if (asker == tableView)
    {   
        BOOL isDate = NO;
        int editedColumn = [tableView editedColumn];
        if (editedColumn > -1)
        {
            NSTableColumn *column = [[tableView tableColumns] objectAtIndex:editedColumn];
            NSString *name = [column identifier];
            isDate = [name isEqualTo:@"date"];
        }
        return isDate ? (id)customDateFieldEditor : (id)customFieldEditor;
    }
    return nil;
}

- (void)showBalanceGraph
{
    [self showGraph:balanceGraph];
}

- (void)showBarGraph
{
    [self showGraph:barGraph];
}


/* Callbacks for python */

- (void)refresh
{
    [columnsManager setColumn:@"balance" visible:[[self py] shouldShowBalanceColumn]];
    [super refresh];
    [totalsLabel setStringValue:[[self py] totals]];
}

@end
