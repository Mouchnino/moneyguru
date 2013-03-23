/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGReadOnlyPluginView.h"
#import "MGTablePrint.h"
#import "Utils.h"

@implementation MGReadOnlyPluginView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyReadOnlyPluginView *m = [[PyReadOnlyPluginView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    tableView = [[MGTableView alloc] initWithFrame:NSMakeRect(0, 0, 100, 100)];
    [self setupTableView:tableView];
    [tableView setAllowsMultipleSelection:YES];
    mainResponder = tableView;
    self.view = [tableView wrapInScrollView];
    table = [[MGTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    HSColumnDef columnModel = {nil, 100, 20, 0, YES, nil};
    [[table columns] initializeColumnsFromModel:columnModel];
    [tableView release];
    return self;
}
        
- (void)dealloc
{
    [table release];
    [super dealloc];
}

- (PyReadOnlyPluginView *)model
{
    return (PyReadOnlyPluginView *)model;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGTablePrint alloc] initWithPyParent:[self model] tableView:[table tableView]] autorelease];
}
@end