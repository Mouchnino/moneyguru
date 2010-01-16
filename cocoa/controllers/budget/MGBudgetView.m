/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGBudgetView.h"
#import "MGBudgetPrint.h"
#import "MGUtils.h"

@implementation MGBudgetView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"BudgetTable" owner:self];
    budgetTable = [[MGBudgetTable alloc] initWithDocument:aDocument view:tableView];
    NSArray *children = [NSArray arrayWithObjects:[budgetTable py], nil];
    Class pyClass = [MGUtils classNamed:@"PyBudgetView"];
    py = [[pyClass alloc] initWithCocoa:self pyParent:[aDocument py] children:children];
    return self;
}
        
- (void)dealloc
{
    [py release];
    [budgetTable release];
    [super dealloc];
}

- (oneway void)release
{
    if ([self retainCount] == 2)
        [py free];
    [super release];
}

- (PyBudgetView *)py
{
    return (PyBudgetView *)py;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGBudgetPrint alloc] initWithPyParent:[budgetTable py] tableView:[budgetTable tableView]] autorelease];
}
@end