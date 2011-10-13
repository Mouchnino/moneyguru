/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGEmptyView.h"
#import "MGConst.h"
#import "Utils.h"

@implementation MGEmptyView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyEmptyView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"NewTabView" owner:self];
    return self;
}
        
- (PyEmptyView *)py
{
    return (PyEmptyView *)py;
}

/* Actions */
- (IBAction)selectNetWorthView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeNetWorth];
}

- (IBAction)selectProfitView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeProfit];
}

- (IBAction)selectTransactionView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeTransaction];
}

- (IBAction)selectScheduleView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeSchedule];
}

- (IBAction)selectBudgetView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeBudget];
}

- (IBAction)selectCashculatorView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeCashculator];
}

- (IBAction)selectGeneralLedgerView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeGeneralLedger];
}

- (IBAction)selectDocPropsView:(id)sender
{
    [[self py] selectPaneType:MGPaneTypeDocProps];
}

@end