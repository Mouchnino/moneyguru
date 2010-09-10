/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGeneralLedgerTable.h"
#import "MGTableView.h"
#import "MGReconciliationCell.h"
#import "Utils.h"

@implementation MGGeneralLedgerTable
- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyGeneralLedgerTable" pyParent:aPyParent view:aTableView];
    [self initializeColumns];
    [aTableView setSortDescriptors:[NSArray array]];
    return self;
}

- (void)initializeColumns
{
    MGColumnDef defs[] = {
        {@"status", @"", 16, 16, 16, NO, [MGReconciliationCell class]},
        {@"date", @"Date", 80, 60, 0, NO, nil},
        // {@"reconciliation_date", @"Reconciliation Date", 110, 60, 0, NO, nil},
        // {@"checkno", @"Check #", 72, 40, 0, NO, nil},
        {@"description", @"Description", 278, 80, 0, NO, nil},
        // {@"payee", @"Payee", 80, 80, 0, NO, nil},
        {@"transfer", @"Transfer", 140, 80, 0, NO, nil},
        {@"debit", @"Debit", 80, 80, 0, NO, nil},
        {@"credit", @"Credit", 80, 80, 0, NO, nil},
        {@"balance", @"Balance", 90, 90, 0, NO, nil},
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
- (PyGeneralLedgerTable *)py
{
    return (PyGeneralLedgerTable *)py;
}

/* Delegate */
- (BOOL)tableView:(NSTableView *)tableView isGroupRow:(NSInteger)row
{
    return [[self py] isAccountRow:row];
}

- (id)tableView:(NSTableView *)aTableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    if ([[column identifier] isEqualToString:@"status"]) {
        return nil; // special column
    }
    if ([[self py] isAccountRow:row]) {
        return [[self py] valueForColumn:@"account_name" row:row];;
    }
    return [super tableView:aTableView objectValueForTableColumn:column row:row];
}

- (void)tableView:(NSTableView *)aTableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows]) {
        return;
    }
    if ([[self py] isAccountRow:row]) {
        return;
    }
    if ([aCell isKindOfClass:[NSTextFieldCell class]]) {
        NSTextFieldCell *cell = aCell;
        NSFont *font = [cell font];
        NSFontManager *fontManager = [NSFontManager sharedFontManager];
        BOOL isBold = [[self py] isBoldRow:row];
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
        [cell setReconciled:n2b([[self py] valueForColumn:@"reconciled" row:row])];
        [cell setRecurrent:n2b([[self py] valueForColumn:@"recurrent" row:row])];
        [cell setIsBudget:n2b([[self py] valueForColumn:@"is_budget" row:row])];
    }
}
@end