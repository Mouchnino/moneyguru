/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGExportAccountTable.h"
#import "MGTableView.h"

@implementation MGExportAccountTable
- (id)initWithPyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyExportAccountTable" pyParent:aPyParent view:aTableView];
    [self initializeColumns];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"name", @"Account", 100, 20, 0, NO, nil},
        {@"export", @"Export", 60, 60, 60, NO, [NSButtonCell class]},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"name"];    
    [c setResizingMask:NSTableColumnAutoresizingMask];
    c = [[self tableView] tableColumnWithIdentifier:@"export"];
    [[c dataCell] setButtonType:NSSwitchButton];
    [[c dataCell] setControlSize:NSSmallControlSize];
    [c setResizingMask:NSTableColumnNoResizing];
    [[self tableView] sizeToFit];
}
@end