/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTable.h"
#import "Utils.h"

@implementation MGTable
- (id)initWithPyClassName:(NSString *)aClassName pyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:aClassName pyParent:aPyParent];
    tableView = aTableView;
    [tableView setDataSource:self];
    [tableView setDelegate:self];
    return self;
}

/* MGGUIController */
- (PyTable *)py
{
    return (PyTable *)py;
}

- (NSView *)view
{
    return tableView;
}

/* Data source */

- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [[self py] numberOfRows];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows])
    {
        return @"";
    }
    return [[self py] valueForColumn:[column identifier] row:row];
}

/* NSTableView Delegate */

- (void)tableView:(NSTableView *)aTableView didClickTableColumn:(NSTableColumn *)column
{
    if ([[aTableView sortDescriptors] count] == 0)
        return;
    NSSortDescriptor *sd = [[aTableView sortDescriptors] objectAtIndex:0];
    [[self py] sortByColumn:[sd key] desc:![sd ascending]];
}

// See MGOutline.outlineViewSelectionIsChanging: to know why we update selection in both notifs
- (void)tableViewSelectionIsChanging:(NSNotification *)notification
{
    NSArray *selection = [Utils indexSet2Array:[[self tableView] selectedRowIndexes]];
    NSArray *pyselection = [[self py] selectedRows];
    if (![selection isEqualTo:pyselection])
        [[self py] selectRows:selection];
}

- (void)tableViewSelectionDidChange:(NSNotification *)notification
{
    NSArray *selection = [Utils indexSet2Array:[[self tableView] selectedRowIndexes]];
    NSArray *pyselection = [[self py] selectedRows];
    if (![selection isEqualTo:pyselection])
        [[self py] selectRows:selection];
}

/* MGTableView delegate */

- (NSIndexSet *)selectedIndexes
{
    return [Utils array2IndexSet:[[self py] selectedRows]];
}

/* Public */

- (MGTableView *)tableView
{
    return tableView;
}

- (void)refresh
{
    // If we just deleted the last item, we want to update the selection before we reload
    [[self tableView] updateSelection];
    [[self tableView] reloadData];
    [[self tableView] updateSelection];
}

- (void)showSelectedRow
{
    [[self tableView] scrollRowToVisible:[[self tableView] selectedRow]];
}

- (void)updateSelection
{
    [[self tableView] updateSelection];
}

@end
