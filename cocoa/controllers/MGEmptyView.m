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
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyEmptyView *m = [[PyEmptyView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    [NSBundle loadNibNamed:@"NewTabView" owner:self];
    return self;
}
        
- (PyEmptyView *)model
{
    return (PyEmptyView *)model;
}

/* Actions */
- (IBAction)selectNetWorthView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeNetWorth];
}

- (IBAction)selectProfitView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeProfit];
}

- (IBAction)selectTransactionView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeTransaction];
}

- (IBAction)selectScheduleView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeSchedule];
}

- (IBAction)selectBudgetView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeBudget];
}

- (IBAction)selectCashculatorView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeCashculator];
}

- (IBAction)selectGeneralLedgerView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeGeneralLedger];
}

- (IBAction)selectDocPropsView:(id)sender
{
    [[self model] selectPaneType:MGPaneTypeDocProps];
}

@end