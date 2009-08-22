/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGBudgetTable.h"
#import "MGTableView.h"

@implementation MGBudgetTable
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyBudgetTable" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"BudgetTable" owner:self];
    return self;
}

/* Overrides */
- (PyBudgetTable *)py
{
    return (PyBudgetTable *)py;
}

/* Delegate */
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