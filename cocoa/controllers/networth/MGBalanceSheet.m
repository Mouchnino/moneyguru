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
- (id)initWithPyRef:(PyObject *)aPyRef view:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyRef:aPyRef view:aOutlineView];
    [self initializeColumns];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        /* Account column is defined in XIB */
        {@"account_number", 64, 10, 0, NO, nil},
        {@"end", 100, 10, 0, NO, [MGAmountCell class]},
        {@"delta", 100, 10, 0, NO, [MGAmountCell class]},
        {@"delta_perc", 60, 10, 0, NO, [MGAmountCell class]},
        {@"start", 100, 10, 0, NO, [MGAmountCell class]},
        {@"budgeted", 100, 10, 0, NO, [MGAmountCell class]},
        nil
    };
    [[self columns] initializeColumns:defs];
    for (NSTableColumn *c in [[self view] tableColumns]) {
        [c setEditable:NO];
    }
    NSTableColumn *c = [[self view] tableColumnWithIdentifier:@"name"];
    [c setEditable:YES]; // Only account name is editable.
    c = [[self view] tableColumnWithIdentifier:@"end"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    NSFontManager *fontManager = [NSFontManager sharedFontManager];
    NSFont *font = [[c dataCell] font];
    font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
    [[c dataCell] setFont:font];
    c = [[self view] tableColumnWithIdentifier:@"delta"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self view] tableColumnWithIdentifier:@"delta_perc"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self view] tableColumnWithIdentifier:@"start"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self view] tableColumnWithIdentifier:@"budgeted"];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}
@end 
