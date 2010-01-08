/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTransactionTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGFieldEditor.h"
#import "MGReconciliationCell.h"
#import "MGTextFieldCell.h"
#import "MGTransactionPrint.h"

@implementation MGTransactionTable

- (id)initWithDocument:(MGDocument *)aDocument view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyTransactionTable" pyParent:[aDocument py] view:aTableView];
    [[self tableView] registerForDraggedTypes:[NSArray arrayWithObject:MGTransactionPasteboardType]];
    // Table auto-save also saves sort descriptors, but we want them to be reset to date on startup
    NSSortDescriptor *sd = [[[NSSortDescriptor alloc] initWithKey:@"date" ascending:YES] autorelease];
    [[self tableView] setSortDescriptors:[NSArray arrayWithObject:sd]];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:[self tableView]];
    [columnsManager linkColumn:@"description" toUserDefault:TransactionDescriptionColumnVisible];
    [columnsManager linkColumn:@"payee" toUserDefault:TransactionPayeeColumnVisible];
    [columnsManager linkColumn:@"checkno" toUserDefault:TransactionChecknoColumnVisible];
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

/* Overrides */

- (PyTransactionTable *)py
{
    return (PyTransactionTable *)py;
}

- (NSView *)viewToPrint
{
    return [[[MGTransactionPrint alloc] initWithPyParent:py tableView:[self tableView]] 
        autorelease];
}

/* Data source */

- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:MGTransactionPasteboardType] owner:self];
    [pboard setData:data forType:MGTransactionPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(int)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropAbove)
    {
        NSPasteboard* pboard = [info draggingPasteboard];
        NSData* rowData = [pboard dataForType:MGTransactionPasteboardType];
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
    NSData* rowData = [pboard dataForType:MGTransactionPasteboardType];
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
        return; // special column
    }
    [super tableView:aTableView setObjectValue:value forTableColumn:column row:row];
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
            isDate = [name isEqualTo:@"date"];
        }
        return isDate ? (id)customDateFieldEditor : (id)customFieldEditor;
    }
    return nil;
}

- (void)showFromAccount:(id)sender
{
    [[self py] showFromAccount];
}

- (void)showToAccount:(id)sender
{
    [[self py] showToAccount];
}

/* Delegate */
- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(int)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows])
    {
        return;
    }
    if ([[column identifier] isEqualToString:@"status"])
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
        [cell setRecurrent:n2b([[self py] valueForColumn:@"recurrent" row:row])];
        [cell setIsBudget:n2b([[self py] valueForColumn:@"is_budget" row:row])];
        [cell setReconciled:n2b([[self py] valueForColumn:@"reconciled" row:row])];
    }
    if (([[column identifier] isEqualToString:@"from"]) || ([[column identifier] isEqualToString:@"to"]))
    {
        MGTextFieldCell *cell = aCell;
        BOOL isFocused = aTableView == [[aTableView window] firstResponder] && [[aTableView window] isKeyWindow];
        BOOL isSelected = row == [aTableView selectedRow];
        [cell setHasArrow:YES];
        [cell setArrowTarget:self];
        if ([[column identifier] isEqualToString:@"from"])
            [cell setArrowAction:@selector(showFromAccount:)];
        else
            [cell setArrowAction:@selector(showToAccount:)];
        [cell setHasDarkBackground:isSelected && isFocused];
    }
}

/* Callbacks for python */

- (void)refresh
{
    [super refresh];
    // [totalsLabel setStringValue:[[self py] totals]];
}


@end