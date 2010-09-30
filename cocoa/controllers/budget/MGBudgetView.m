/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBudgetView.h"
#import "MGBudgetPrint.h"
#import "Utils.h"

@implementation MGBudgetView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyBudgetView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"BudgetTable" owner:self];
    budgetTable = [[MGBudgetTable alloc] initWithPyParent:[self py] view:tableView];
    NSArray *children = [NSArray arrayWithObjects:[budgetTable py], nil];
    [[self py] setChildren:children];
    return self;
}
        
- (void)dealloc
{
    [budgetTable release];
    [super dealloc];
}

- (PyBudgetView *)py
{
    return (PyBudgetView *)py;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGBudgetPrint alloc] initWithPyParent:[self py] tableView:[budgetTable tableView]] autorelease];
}
@end