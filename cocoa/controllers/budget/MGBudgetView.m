/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBudgetView.h"
#import "MGBudgetPrint.h"
#import "Utils.h"

@implementation MGBudgetView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyBudgetView *m = [[PyBudgetView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    tableView = [[MGTableView alloc] initWithFrame:NSMakeRect(0, 0, 100, 100)];
    [self setupTableView:tableView];
    mainResponder = tableView;
    wholeView = [[tableView wrapInScrollView] retain];
    budgetTable = [[MGBudgetTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    [tableView release];
    return self;
}
        
- (void)dealloc
{
    [budgetTable release];
    [wholeView release];
    [super dealloc];
}

- (PyBudgetView *)model
{
    return (PyBudgetView *)model;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGBudgetPrint alloc] initWithPyParent:[self model] tableView:[budgetTable tableView]] autorelease];
}

- (NSString *)tabIconName
{
    return @"budget_16";
}
@end