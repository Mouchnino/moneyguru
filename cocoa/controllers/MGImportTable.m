/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGImportTable.h"
#import "Utils.h"
#import "ObjP.h"
#import "MGConst.h"
#import "MGImportBindingCell.h"

@implementation MGImportTable
- (id)initWithPy:(id)aPy view:(MGTableView *)aTableView
{
    PyObject *pRef = getHackedPyRef(aPy);
    PyImportTable *m = [[PyImportTable alloc] initWithModel:pRef];
    OBJP_LOCKGIL;
    Py_DECREF(pRef);
    OBJP_UNLOCKGIL;
    self = [super initWithModel:m tableView:aTableView];
    [m bindCallback:createCallback(@"TableView", self)];
    [m release];
    [self initializeColumns];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGImportEntryPasteboardType]];
    NSTableColumn *boundColumn = [[aTableView tableColumns] objectAtIndex:4];
    NSActionCell *cell = [boundColumn dataCell];
    [cell setTarget:self];
    [cell setAction:@selector(bindLockClick:)];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"will_import", 14, 14, 14, NO, [NSButtonCell class]},
        {@"date", 80, 40, 0, NO, nil},
        {@"description", 100, 40, 0, NO, nil},
        {@"amount", 80, 10, 0, NO, nil},
        {@"bound", 14, 14, 14, NO, [MGImportBindingCell class]},
        {@"date_import", 80, 10, 0, NO, nil},
        {@"description_import", 100, 10, 0, NO, nil},
        {@"payee_import", 80, 10, 0, NO, nil},
        {@"checkno_import", 60, 10, 0, NO, nil},
        {@"transfer_import", 110, 10, 0, NO, nil},
        {@"amount_import", 80, 10, 0, NO, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"will_import"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    c = [[self tableView] tableColumnWithIdentifier:@"bound"];
    /* I'm not too sure why NSSwitchButton type is needed here, but it is (otherwise clicking on
       the cell has no effect).
    */
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    [[c dataCell] setBordered:NO];
    c = [[self tableView] tableColumnWithIdentifier:@"amount"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"amount_import"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
}

- (PyImportTable *)model
{
    return (PyImportTable *)model;
}


- (void)updateOneOrTwoSided
{
    BOOL shouldShow = [[self model] isTwoSided];
    NSArray *colnames = [NSArray arrayWithObjects:@"date", @"description", @"amount", @"bound", nil];
    for (NSString *colname in colnames) {
        NSTableColumn *col = [[self tableView] tableColumnWithIdentifier:colname];
        [col setHidden:!shouldShow];
    }
}

/* About NSTableView and NSActionCell

From what I can understand, actions from an action cell is a tableview happen *after* the selectedRow
has changed, but *before* tableViewSelectionDidChange. At first, I had a unbindSelectedRow, but it
didn't work. We have to use [tableView selectedRow] to know which row to unbind.
*/
- (void)bindLockClick:(id)sender
{
    [[self model] unbindRow:[[self tableView] selectedRow]];
}

/* Delegate */
- (void)tableView:(NSTableView *)aTableView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    NSString *colname = [column identifier];
    if ([colname isEqualToString:@"bound"])
        return; // Don't send any value down to the model.
    [super tableView:aTableView setObjectValue:value forTableColumn:column row:row];
}

- (void)tableView:(NSTableView *)tableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self model] numberOfRows])
        return;
    NSString *colname = [column identifier];
    if ([colname isEqualToString:@"will_import"]) {
        BOOL canEdit = n2b([[self model] canEditColumn:@"will_import" atRow:row]);
        [aCell setEnabled:canEdit];
        return;
    }
}

- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:MGImportEntryPasteboardType] owner:self];
    [pboard setData:data forType:MGImportEntryPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(NSInteger)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropOn)
    {
        NSPasteboard* pboard = [info draggingPasteboard];
        NSData* rowData = [pboard dataForType:MGImportEntryPasteboardType];
        NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
        NSInteger source = [rowIndexes firstIndex];
        if ([[self model] canBindRow:source to:row])
        {
            return NSDragOperationMove;
        }
    }
    return NSDragOperationNone;
}

- (BOOL)tableView:(NSTableView *)aTableView acceptDrop:(id <NSDraggingInfo>)info
              row:(NSInteger)row dropOperation:(NSTableViewDropOperation)operation
{
    NSPasteboard* pboard = [info draggingPasteboard];
    NSData* rowData = [pboard dataForType:MGImportEntryPasteboardType];
    NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    NSInteger source = [rowIndexes firstIndex];
    [[self model] bindRow:source to:row];
    return YES;
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self model] toggleImportStatus];
    return YES;
}

- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    return YES;
}
@end