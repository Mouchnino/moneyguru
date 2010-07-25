/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGScheduleTable.h"
#import "MGConst.h"
#import "MGTableView.h"

@implementation MGScheduleTable
- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyScheduleTable" pyParent:aPyParent view:aTableView];
    [self initializeColumns];
    [aTableView setSortDescriptors:[NSArray array]];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:aTableView];
    [columnsManager linkColumn:@"description" toUserDefault:ScheduleDescriptionColumnVisible];
    [columnsManager linkColumn:@"payee" toUserDefault:SchedulePayeeColumnVisible];
    [columnsManager linkColumn:@"checkno" toUserDefault:ScheduleChecknoColumnVisible];
    return self;
}

- (void)initializeColumns
{
    MGColumnDef defs[] = {
        {@"start_date", @"Start Date", 80, 60, 0, YES, nil},
        {@"stop_date", @"Stop Date", 80, 60, 0, YES, nil},
        {@"repeat_type", @"Repeat Type", 80, 60, 0, YES, nil},
        {@"interval", @"Interval", 60, 60, 0, YES, nil},
        {@"checkno", @"Check #", 72, 40, 0, YES, nil},
        {@"description", @"Description", 310, 80, 0, YES, nil},
        {@"payee", @"Payee", 85, 80, 0, YES, nil},
        {@"from", @"From", 136, 70, 0, YES, nil},
        {@"to", @"To", 135, 70, 0, YES, nil},
        {@"amount", @"Amount", 90, 80, 0, YES, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"amount"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
}

/* Overrides */
- (PyScheduleTable *)py
{
    return (PyScheduleTable *)py;
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