/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGScheduleTable.h"
#import "MGConst.h"
#import "MGTableView.h"
#import "Utils.h"

@implementation MGScheduleTable
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(MGTableView *)aTableView
{
    PyScheduleTable *m = [[PyScheduleTable alloc] initWithModel:aPyRef];
    self = [super initWithModel:m tableView:aTableView];
    [m bindCallback:createCallback(@"TableView", self)];
    [m release];
    [self initializeColumns];
    [aTableView setSortDescriptors:[NSArray array]];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"start_date", 80, 60, 0, YES, nil},
        {@"stop_date", 80, 60, 0, YES, nil},
        {@"repeat_type", 80, 60, 0, YES, nil},
        {@"interval", 60, 60, 0, YES, nil},
        {@"checkno", 72, 40, 0, YES, nil},
        {@"description", 150, 80, 0, YES, nil},
        {@"payee", 85, 80, 0, YES, nil},
        {@"from", 118, 70, 0, YES, nil},
        {@"to", 118, 70, 0, YES, nil},
        {@"amount", 90, 80, 0, YES, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"amount"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    [[self columns] restoreColumns];
}

/* Overrides */
- (PyScheduleTable *)model
{
    return (PyScheduleTable *)model;
}

/* Delegate */
- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView
{
    [[self model] deleteSelectedRows];
    return YES;
}

- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [[self model] editItem];
    return YES;
}

- (void)tableViewWasDoubleClicked:(MGTableView *)tableView
{
    [[self model] editItem];
}
@end