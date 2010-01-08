/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGBudgetView.h"

@implementation MGBudgetView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"BudgetTable" owner:self];
    budgetTable = [[MGBudgetTable alloc] initWithDocument:aDocument view:tableView];
    return self;
}
        
- (void)dealloc
{
    [budgetTable release];
    [super dealloc];
}

- (NSView *)view
{
    return wholeView;
}

- (MGPrintView *)viewToPrint
{
    return [budgetTable viewToPrint];
}

- (void)connect
{
    [budgetTable connect];
}

- (void)disconnect
{
    [budgetTable disconnect];
}

- (MGBudgetTable *)budgetTable
{
    return budgetTable;
}
@end