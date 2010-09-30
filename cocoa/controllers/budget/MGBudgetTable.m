/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBudgetTable.h"
#import "MGTableView.h"

@implementation MGBudgetTable
- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyBudgetTable" pyParent:aPyParent view:aTableView];
    [self initializeColumns];
    [aTableView setSortDescriptors:[NSArray array]];
    return self;
}

- (void)initializeColumns
{
    MGColumnDef defs[] = {
        {@"start_date", @"Start Date", 80, 60, 0, YES, nil},
        {@"stop_date", @"Stop Date", 80, 60, 0, YES, nil},
        {@"repeat_type", @"Repeat Type", 80, 60, 0, YES, nil},
        {@"interval", @"Interval", 60, 60, 0, YES, nil},
        {@"account", @"Account", 136, 70, 0, YES, nil},
        {@"target", @"Target", 120, 70, 0, YES, nil},
        {@"amount", @"Amount", 90, 80, 0, YES, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"amount"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

/* Overrides */
- (PyBudgetTable *)py
{
    return (PyBudgetTable *)py;
}

/* Delegate */
- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView
{
    [[self py] deleteSelectedRows];
    return YES;
}

- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [[self py] editItem];
    return YES;
}

- (void)tableViewWasDoubleClicked:(MGTableView *)tableView
{
    [[self py] editItem];
}
@end