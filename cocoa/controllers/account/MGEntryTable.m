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

- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyEntryTable" pyParent:aPyParent view:aTableView];
    [self initializeColumns];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGEntryPasteboardType]];
    // Table auto-save also saves sort descriptors, but we want them to be reset to date on startup
    NSSortDescriptor *sd = [[[NSSortDescriptor alloc] initWithKey:@"date" ascending:YES] autorelease];
    [aTableView setSortDescriptors:[NSArray arrayWithObject:sd]];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:aTableView];
    [columnsManager linkColumn:@"description" toUserDefault:AccountDescriptionColumnVisible];
    [columnsManager linkColumn:@"payee" toUserDefault:AccountPayeeColumnVisible];
    [columnsManager linkColumn:@"checkno" toUserDefault:AccountChecknoColumnVisible];
    [columnsManager linkColumn:@"reconciliation_date" toUserDefault:AccountReconciliationDateColumnVisible];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyParent:aPyParent];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    return self;
}

- (void)initializeColumns
{
    MGColumnDef defs[] = {
        {@"status", @"", 16, 16, 16, NO, [MGReconciliationCell class]},
        {@"date", @"Date", 80, 60, 0, YES, nil},
        {@"reconciliation_date", @"Reconciliation Date", 110, 60, 0, YES, nil},
        {@"checkno", @"Check #", 72, 40, 0, YES, nil},
        {@"description", @"Description", 278, 80, 0, YES, nil},
        {@"payee", @"Payee", 80, 80, 0, YES, nil},
        {@"transfer", @"Transfer", 140, 80, 0, YES, [MGTextFieldCell class]},
        {@"increase", @"Increase", 80, 80, 0, YES, nil},
        {@"decrease", @"Decrease", 80, 80, 0, YES, nil},
        {@"balance", @"Balance", 90, 90, 0, YES, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"status"];
    [c setResizingMask:NSTableColumnNoResizing];
    [[c dataCell] setImagePosition:NSImageOnly];
    [[c dataCell] setBordered:NO];
    c = [[self tableView] tableColumnWithIdentifier:@"increase"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"decrease"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"balance"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

- (void)dealloc
{
    [customFieldEditor release];
    [customDateFieldEditor release];
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

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(NSInteger)row 
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
              row:(NSInteger)row dropOperation:(NSTableViewDropOperation)operation
{
    NSPasteboard* pboard = [info draggingPasteboard];
    NSData* rowData = [pboard dataForType:MGEntryPasteboardType];
    NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    [[self py] moveRows:[Utils indexSet2Array:rowIndexes] to:row];
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
        if ([[self py] canReconcileEntryAtRow:row])
        {
            [[self py] toggleReconciledAtRow:row];
        }
        return;
    }
    [super tableView:aTableView setObjectValue:value forTableColumn:column row:row];
}

/* Delegate */

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows]) {
        return;
    }
    if ([aCell isKindOfClass:[NSTextFieldCell class]]) {
        NSTextFieldCell *cell = aCell;
        NSFont *font = [cell font];
        NSFontManager *fontManager = [NSFontManager sharedFontManager];
        BOOL isBold = [[self py] isBoldAtRow:row];
        if (isBold) {
            font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
        }
        else {
            font = [fontManager convertFont:font toNotHaveTrait:NSFontBoldTrait];
        }
        [cell setFont:font];
    }
    if ([[column identifier] isEqualToString:@"balance"]) {
        NSColor *color = [[self py] isBalanceNegativeAtRow:row] ? [NSColor redColor] : [NSColor blackColor];
        [aCell setTextColor:color];
    }
    else if ([[column identifier] isEqualToString:@"status"]) {
        MGReconciliationCell *cell = aCell;
        if (row == [[self tableView] editedRow]) {
            [cell setIsInFuture:[[self py] isEditedRowInTheFuture]];
            [cell setIsInPast:[[self py] isEditedRowInThePast]];
        }
        else {
            [cell setIsInFuture:NO];
            [cell setIsInPast:NO];
        }
        [cell setCanReconcile:[[self py] canReconcileEntryAtRow:row]];
        [cell setReconciled:n2b([[self py] valueForColumn:@"reconciled" row:row])];
        [cell setRecurrent:n2b([[self py] valueForColumn:@"recurrent" row:row])];
        [cell setIsBudget:n2b([[self py] valueForColumn:@"is_budget" row:row])];
    }
    else if ([[column identifier] isEqualToString:@"transfer"]) {
        MGTextFieldCell *cell = aCell;
        BOOL isFocused = aTableView == [[aTableView window] firstResponder] && [[aTableView window] isKeyWindow];
        BOOL isSelected = row == [aTableView selectedRow];
        BOOL isPrinting = [NSPrintOperation currentOperation] != nil;
        if (isPrinting) {
            [cell setHasArrow:NO];
        } else {
            [cell setHasArrow:YES];
            [cell setArrowTarget:self];
            [cell setArrowAction:@selector(showTransferAccount:)];
            [cell setHasDarkBackground:isSelected && isFocused];
        }
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
    if (asker == [self tableView]) {   
        NSInteger editedColumn = [[self tableView] editedColumn];
        if (editedColumn > -1) {
            NSTableColumn *column = [[[self tableView] tableColumns] objectAtIndex:editedColumn];
            NSString *name = [column identifier];
            if ([name isEqualTo:@"date"] || [name isEqualTo:@"reconciliation_date"]) {
                return customDateFieldEditor;
            }
            else if ([name isEqualTo:@"description"] || [name isEqualTo:@"payee"] || [name isEqualTo:@"transfer"]) {
                [customFieldEditor setAttrname:name];
                return customFieldEditor;
            }
        }
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
}

@end
