/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGBalanceSheet.h"
#import "MGConst.h"

@implementation MGBalanceSheet
- (id)initWithPyParent:(id)aPyParent view:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyParent:aPyParent pyClassName:@"PyBalanceSheet" view:aOutlineView];
    [self setAutosaveName:@"BalanceSheet"];
    columnsManager = [[HSTableColumnManager alloc] initWithTable:aOutlineView];
    [columnsManager linkColumn:@"delta" toUserDefault:BalanceSheetDeltaColumnVisible];
    [columnsManager linkColumn:@"delta_perc" toUserDefault:BalanceSheetDeltaPercColumnVisible];
    [columnsManager linkColumn:@"start" toUserDefault:BalanceSheetStartColumnVisible];
    [columnsManager linkColumn:@"budgeted" toUserDefault:BalanceSheetBudgetedColumnVisible];
    [columnsManager linkColumn:@"account_number" toUserDefault:BalanceSheetAccountNumberColumnVisible];
    return self;
}

- (void)dealloc
{
    [columnsManager release];
    [super dealloc];
}

/* Overrides */
- (PyBalanceSheet *)py
{
    return (PyBalanceSheet *)py;
}
@end 
