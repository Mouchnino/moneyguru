/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGEntryTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGTableView.h"
#import "MGReconciliationCell.h"
#import "MGTextFieldCell.h"

@implementation MGEntryTable

- (id)initWithDocument:(MGDocument *)aDocument view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyEntryTable" pyParent:[aDocument py] view:aTableView];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGEntryPasteboardType]];
    // Table auto-save also saves sort descriptors, but we want them to be reset to date on startup
    NSSortDescriptor *sd = [[[NSSortDescriptor alloc] initWithKey:@"date" ascending:YES] autorelease];
    [aTableView setSortDescriptors:[NSArray arrayWithObject:sd]];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:aTableView];
    [columnsManager linkColumn:@"description" toUserDefault:AccountDescriptionColumnVisible];
    [columnsManager linkColumn:@"payee" toUserDefault:AccountPayeeColumnVisible];
    [columnsManager linkColumn:@"checkno" toUserDefault:AccountChecknoColumnVisible];
    [columnsManager linkColumn:@"reconciliation_date" toUserDefault:AccountReconciliationDateColumnVisible];
    customFieldEditor = [[MGFieldEditor alloc] init];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    [self changeColumns]; // initial set
    return self;
}
        
- (void)dealloc
{
    [customFieldEditor release];
    [columnsManager release];
    [super dealloc];
}

/* Override */

- (PyEntryTable *)py
{
    return (PyEntryTable *)py;
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

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(int)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows])
    {
        return;
    }
    if ([[column identifier] isEqualToString:@"balance"])
    {
        NSColor *color = [[self py] isBalanceNegativeAtRow:row] ? [NSColor redColor] : [NSColor blackColor];
        [aCell setTextColor:color];
    }
    else if ([[column identifier] isEqualToString:@"status"])
    {
        MGReconciliationCell *cell = aCell;
        if (row == [[self tableView] editedRow])
        {
            [cell setIsInFuture:[[self py] isEditedRowInTheFuture]];
            [cell setIsInPast:[[self py] isEditedRowInThePast]];
        }
        else
        {
            [cell setIsInFuture:NO];
            [cell setIsInPast:NO];
        }
        [cell setCanReconcile:[[self py] canReconcileEntryAtRow:row]];
        [cell setReconciled:n2b([[self py] valueForColumn:@"reconciled" row:row])];
        [cell setReconciliationPending:n2b([[self py] valueForColumn:@"reconciliation_pending" row:row])];
        [cell setRecurrent:n2b([[self py] valueForColumn:@"recurrent" row:row])];
        [cell setIsBudget:n2b([[self py] valueForColumn:@"is_budget" row:row])];
    }
    else if ([[column identifier] isEqualToString:@"transfer"])
    {
        MGTextFieldCell *cell = aCell;
        BOOL isFocused = aTableView == [[aTableView window] firstResponder] && [[aTableView window] isKeyWindow];
        BOOL isSelected = row == [aTableView selectedRow];
        [cell setHasArrow:YES];
        [cell setArrowTarget:self];
        [cell setArrowAction:@selector(showTransferAccount:)];
        [cell setHasDarkBackground:isSelected && isFocused];
    }
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self py] toggleReconciled];
    return YES;
}

/* Public */

- (id)fieldEditorForObject:(id)asker
{
    if (asker == [self tableView])
    {   
        BOOL isDate = NO;
        int editedColumn = [[self tableView] editedColumn];
        if (editedColumn > -1)
        {
            NSTableColumn *column = [[[self tableView] tableColumns] objectAtIndex:editedColumn];
            NSString *name = [column identifier];
            isDate = [name isEqualTo:@"date"] || [name isEqualTo:@"reconciliation_date"];
        }
        return isDate ? (id)customDateFieldEditor : (id)customFieldEditor;
    }
    return nil;
}

- (void)showTransferAccount:(id)sender
{
    [[self py] showTransferAccount];
}

/* Callbacks for python */

- (void)refresh
{
    [columnsManager setColumn:@"balance" visible:[[self py] shouldShowBalanceColumn]];
    [super refresh];
    // [totalsLabel setStringValue:[[self py] totals]];
}

@end
