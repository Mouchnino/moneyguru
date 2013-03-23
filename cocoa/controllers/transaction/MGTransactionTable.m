/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGTransactionTable.h"
#import "MGConst.h"
#import "MGFieldEditor.h"
#import "MGReconciliationCell.h"
#import "MGTextFieldCell.h"
#import "HSPyUtil.h"
#import "Utils.h"

@implementation MGTransactionTable
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(MGTableView *)aTableView
{
    PyTransactionTable *m = [[PyTransactionTable alloc] initWithModel:aPyRef];
    self = [super initWithModel:m tableView:aTableView];
    [m bindCallback:createCallback(@"TableView", self)];
    [m release];
    [self initializeColumns];
    [[self tableView] registerForDraggedTypes:[NSArray arrayWithObject:MGTransactionPasteboardType]];
    // Table auto-save also saves sort descriptors, but we want them to be reset to date on startup
    NSSortDescriptor *sd = [[[NSSortDescriptor alloc] initWithKey:@"date" ascending:YES] autorelease];
    [[self tableView] setSortDescriptors:[NSArray arrayWithObject:sd]];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"status", 16, 16, 16, NO, [MGReconciliationCell class]},
        {@"date", 80, 60, 0, YES, nil},
        {@"checkno", 72, 40, 0, YES, nil},
        {@"description", 310, 80, 0, YES, nil},
        {@"payee", 85, 80, 0, YES, nil},
        {@"from", 136, 70, 0, YES, [MGTextFieldCell class]},
        {@"to", 135, 70, 0, YES, [MGTextFieldCell class]},
        {@"amount", 90, 70, 0, YES, nil},
        {@"mtime", 140, 50, 0, YES, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"status"];
    [c setResizingMask:NSTableColumnNoResizing];
    [[c dataCell] setImagePosition:NSImageOnly];
    [[c dataCell] setBordered:NO];
    c = [[self tableView] tableColumnWithIdentifier:@"amount"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

/* Overrides */

- (PyTransactionTable *)model
{
    return (PyTransactionTable *)model;
}

- (NSArray *)dateColumns
{
    return [NSArray arrayWithObjects:@"date", nil];
}

- (NSArray *)completableColumns
{
    return [NSArray arrayWithObjects:@"description", @"payee", @"from", @"to", nil];
}

/* Data source */

- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:MGTransactionPasteboardType] owner:self];
    [pboard setData:data forType:MGTransactionPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(NSInteger)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropAbove)
    {
        NSPasteboard* pboard = [info draggingPasteboard];
        NSData* rowData = [pboard dataForType:MGTransactionPasteboardType];
        NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
        if ([[self model] canMoveRows:[Utils indexSet2Array:rowIndexes] to:row])
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
    NSData* rowData = [pboard dataForType:MGTransactionPasteboardType];
    NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    [[self model] moveRows:[Utils indexSet2Array:rowIndexes] to:row];
    return YES;
}

- (id)tableView:(NSTableView *)aTableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    if ([[column identifier] isEqualToString:@"status"])
    {
        return nil; // special column
    }
    return [super tableView:aTableView objectValueForTableColumn:column row:row];
}

- (void)tableView:(NSTableView *)aTableView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    if ([[column identifier] isEqualToString:@"status"])
    {
        return; // special column
    }
    [super tableView:aTableView setObjectValue:value forTableColumn:column row:row];
}

/* Delegate */
- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self model] numberOfRows]) {
        return;
    }
    if ([aCell isKindOfClass:[NSTextFieldCell class]]) {
        NSTextFieldCell *cell = aCell;
        NSFont *font = [cell font];
        NSFontManager *fontManager = [NSFontManager sharedFontManager];
        BOOL isBold = [[self model] isBoldAtRow:row];
        if (isBold) {
            font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
        }
        else {
            font = [fontManager convertFont:font toNotHaveTrait:NSFontBoldTrait];
        }
        [cell setFont:font];
    }
    if ([[column identifier] isEqualToString:@"status"]) {
        MGReconciliationCell *cell = aCell;
        if (row == [[self tableView] editedRow]) {
            [cell setIsInFuture:[[self model] isEditedRowInTheFuture]];
            [cell setIsInPast:[[self model] isEditedRowInThePast]];
        }
        else {
            [cell setIsInFuture:NO];
            [cell setIsInPast:NO];
        }
        [cell setRecurrent:n2b([[self model] valueForColumn:@"recurrent" row:row])];
        [cell setIsBudget:n2b([[self model] valueForColumn:@"is_budget" row:row])];
        [cell setReconciled:n2b([[self model] valueForColumn:@"reconciled" row:row])];
    }
    if (([[column identifier] isEqualToString:@"from"]) || ([[column identifier] isEqualToString:@"to"])) {
        MGTextFieldCell *cell = aCell;
        BOOL isFocused = aTableView == [[aTableView window] firstResponder] && [[aTableView window] isKeyWindow];
        BOOL isSelected = row == [aTableView selectedRow];
        BOOL isPrinting = [NSPrintOperation currentOperation] != nil;
        if (isPrinting) {
            [cell setHasArrow:NO];
        } else {
            [cell setHasArrow:YES];
            [cell setArrowTarget:[self model]];
            if ([[column identifier] isEqualToString:@"from"])
                [cell setArrowAction:@selector(showFromAccount)];
            else
                [cell setArrowAction:@selector(showToAccount)];
            [cell setHasDarkBackground:isSelected && isFocused];
        }
    }
}
@end