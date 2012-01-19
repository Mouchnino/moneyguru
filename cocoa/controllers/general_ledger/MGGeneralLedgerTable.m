/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGeneralLedgerTable.h"
#import "MGTableView.h"
#import "MGReconciliationCell.h"
#import "Utils.h"
#import "ObjP.h"

@implementation MGGeneralLedgerTable
- (id)initWithPy:(id)aPy tableView:(MGTableView *)aTableView
{
    PyObject *pRef = getHackedPyRef(aPy);
    PyGeneralLedgerTable *m = [[PyGeneralLedgerTable alloc] initWithModel:pRef];
    OBJP_LOCKGIL;
    Py_DECREF(pRef);
    OBJP_UNLOCKGIL;
    self = [super initWithModel:m tableView:aTableView];
    [m bindCallback:createCallback(@"TableView", self)];
    [m release];
    [self initializeColumns];
    [aTableView setSortDescriptors:[NSArray array]];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"status", 16, 16, 16, NO, [MGReconciliationCell class]},
        {@"date", 80, 60, 0, NO, nil},
        {@"reconciliation_date", 110, 60, 0, NO, nil},
        {@"checkno", 72, 40, 0, NO, nil},
        {@"description", 278, 80, 0, NO, nil},
        {@"payee", 80, 80, 0, NO, nil},
        {@"transfer", 140, 80, 0, NO, nil},
        {@"debit", 80, 80, 0, NO, nil},
        {@"credit", 80, 80, 0, NO, nil},
        {@"balance", 90, 90, 0, NO, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"status"];
    NSButtonCell *cell = [c dataCell];
    [c setResizingMask:NSTableColumnNoResizing];
    [cell setBordered:NO];
    [cell setButtonType:NSSwitchButton];
    [cell setControlSize:NSSmallControlSize];
    c = [[self tableView] tableColumnWithIdentifier:@"debit"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"credit"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"balance"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

/* Overrides */
- (PyGeneralLedgerTable *)model
{
    return (PyGeneralLedgerTable *)model;
}

- (NSArray *)dateColumns
{
    return [NSArray arrayWithObjects:@"date", @"reconciliation_date", nil];
}

- (NSArray *)completableColumns
{
    return [NSArray arrayWithObjects:@"description", @"payee", @"transfer", nil];
}

/* Delegate */
- (BOOL)tableView:(NSTableView *)tableView isGroupRow:(NSInteger)row
{
    return [[self model] isAccountRow:row];
}

- (id)tableView:(NSTableView *)aTableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    if ([[column identifier] isEqualToString:@"status"]) {
        return nil; // special column
    }
    if ([[self model] isAccountRow:row]) {
        return [[self model] valueForColumn:@"account_name" row:row];;
    }
    return [super tableView:aTableView objectValueForTableColumn:column row:row];
}

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self model] numberOfRows]) {
        return;
    }
    if ([[self model] isAccountRow:row]) {
        return;
    }
    if ([aCell isKindOfClass:[NSTextFieldCell class]]) {
        NSTextFieldCell *cell = aCell;
        NSFont *font = [cell font];
        NSFontManager *fontManager = [NSFontManager sharedFontManager];
        BOOL isBold = [[self model] isBoldRow:row];
        if (isBold) {
            font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
        }
        else {
            font = [fontManager convertFont:font toNotHaveTrait:NSFontBoldTrait];
        }
        [cell setFont:font];
    }
    else if ([[column identifier] isEqualToString:@"status"]) {
        MGReconciliationCell *cell = aCell;
        [cell setReconciled:n2b([[self model] valueForColumn:@"reconciled" row:row])];
        [cell setRecurrent:n2b([[self model] valueForColumn:@"recurrent" row:row])];
        [cell setIsBudget:n2b([[self model] valueForColumn:@"is_budget" row:row])];
    }
}
@end