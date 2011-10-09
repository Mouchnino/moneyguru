/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBalanceSheet.h"
#import "MGConst.h"
#import "MGAmountCell.h"

@implementation MGBalanceSheet
- (id)initWithPyParent:(id)aPyParent view:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyClassName:@"PyBalanceSheet" pyParent:aPyParent view:aOutlineView];
    [self initializeColumns];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        /* Account column is defined in XIB */
        {@"account_number", @"Account #", 64, 10, 0, NO, nil},
        {@"end", @"End", 100, 10, 0, NO, [MGAmountCell class]},
        {@"delta", @"Change", 100, 10, 0, NO, [MGAmountCell class]},
        {@"delta_perc", @"Change %", 60, 10, 0, NO, [MGAmountCell class]},
        {@"start", @"Start", 100, 10, 0, NO, [MGAmountCell class]},
        {@"budgeted", @"Budgeted", 100, 10, 0, NO, [MGAmountCell class]},
        nil
    };
    [[self columns] initializeColumns:defs];
    for (NSTableColumn *c in [[self outlineView] tableColumns]) {
        [c setEditable:NO];
    }
    NSTableColumn *c = [[self outlineView] tableColumnWithIdentifier:@"name"];
    [c setEditable:YES]; // Only account name is editable.
    c = [[self outlineView] tableColumnWithIdentifier:@"end"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    NSFontManager *fontManager = [NSFontManager sharedFontManager];
    NSFont *font = [[c dataCell] font];
    font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
    [[c dataCell] setFont:font];
    c = [[self outlineView] tableColumnWithIdentifier:@"delta"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self outlineView] tableColumnWithIdentifier:@"delta_perc"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self outlineView] tableColumnWithIdentifier:@"start"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self outlineView] tableColumnWithIdentifier:@"budgeted"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

/* Overrides */
- (PyBalanceSheet *)py
{
    return (PyBalanceSheet *)py;
}
@end 
