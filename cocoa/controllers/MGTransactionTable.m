/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTransactionTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGFieldEditor.h"
#import "MGReconciliationCell.h"
#import "MGTransactionPrint.h"

@implementation MGTransactionTable

- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyTransactionTable" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"TransactionTable" owner:self];
    [tableView registerForDraggedTypes:[NSArray arrayWithObject:MGTransactionPasteboardType]];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:tableView];
    // The 2 lines below are because of OS X Tiger, see MGEntryTable for details
    [tableView setAutosaveName:@"TransactionTable"];
    [tableView setAutosaveTableColumns:YES];
    [columnsManager linkColumn:@"description" toUserDefault:TransactionDescriptionColumnVisible];
    [columnsManager linkColumn:@"payee" toUserDefault:TransactionPayeeColumnVisible];
    [columnsManager linkColumn:@"checkno" toUserDefault:TransactionChecknoColumnVisible];
    customFieldEditor = [[MGFieldEditor alloc] init];
    filterBar = [[MGFilterBar alloc] initWithDocument:aDocument view:filterBarView forEntryTable:NO];
    [self changeColumns]; // initial set
    return self;
}
        
- (void)dealloc
{
    [filterBar release];
    [customFieldEditor release];
    [columnsManager release];
    [super dealloc];
}

/* Overrides */

- (PyTransactionTable *)py
{
    return (PyTransactionTable *)py;
}

- (void)connect
{
    [super connect];
    [filterBar connect];
}

- (void)disconnect
{
    [super disconnect];
    [filterBar disconnect];
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
        [customFieldEditor setDateMode:isDate];
        return customFieldEditor;
    }
    return nil;
}

- (void)makeScheduleFromSelected
{
    [[self py] makeScheduleFromSelected];
}

- (void)moveUp
{
    [[self py] moveUp];
}

- (void)moveDown
{
    [[self py] moveDown];
}

/* Delegate */

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)cell forTableColumn:(NSTableColumn *)column row:(int)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows])
    {
        return;
    }
    if ([[column identifier] isEqualToString:@"status"])
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
        [rcell setRecurrent:n2b([[self py] valueForColumn:@"recurrent" row:row])];
        [rcell setReconciled:n2b([[self py] valueForColumn:@"reconciled" row:row])];
    }
}

/* Callbacks for python */

- (void)refresh
{
    [super refresh];
    [totalsLabel setStringValue:[[self py] totals]];
}


@end