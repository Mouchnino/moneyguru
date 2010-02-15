/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGIncomeStatement.h"
#import "MGConst.h"

@implementation MGIncomeStatement

- (id)initWithDocument:(MGDocument *)aDocument view:(HSOutlineView *)aOutlineView
{
    self = [super initWithDocument:aDocument pyClassName:@"PyIncomeStatement" view:aOutlineView];
    [self setAutosaveName:@"IncomeStatement"];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:aOutlineView];
    [columnsManager linkColumn:@"delta" toUserDefault:IncomeStatementDeltaColumnVisible];
    [columnsManager linkColumn:@"delta_perc" toUserDefault:IncomeStatementDeltaPercColumnVisible];
    [columnsManager linkColumn:@"last_cash_flow" toUserDefault:IncomeStatementLastColumnVisible];
    [columnsManager linkColumn:@"budgeted" toUserDefault:IncomeStatementBudgetedColumnVisible];
    [columnsManager linkColumn:@"account_number" toUserDefault:IncomeStatementAccountNumberColumnVisible];
    return self;
}

- (void)dealloc
{
    [columnsManager release];
    [super dealloc];
}

/* Overrides */

- (PyIncomeStatement *)py
{
    return (PyIncomeStatement *)py;
}
@end 
