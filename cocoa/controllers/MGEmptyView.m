/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGEmptyView.h"
#import "MGEmptyView_UI.h"
#import "MGConst.h"
#import "Utils.h"

@implementation MGEmptyView

@synthesize pluginTableView;

- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyEmptyView *m = [[PyEmptyView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    self.view = createMGEmptyView_UI(self);
    pluginList = [[HSSelectableList alloc] initWithPyRef:[[self model] pluginList] tableView:pluginTableView];
    [pluginTableView setTarget:self];
    [pluginTableView setDoubleAction:@selector(selectPluginView)];
    return self;
}
        
- (PyEmptyView *)model
{
    return (PyEmptyView *)model;
}

/* Actions */
- (void)selectNetWorthView
{
    [[self model] selectPaneType:MGPaneTypeNetWorth];
}

- (void)selectProfitView
{
    [[self model] selectPaneType:MGPaneTypeProfit];
}

- (void)selectTransactionView
{
    [[self model] selectPaneType:MGPaneTypeTransaction];
}

- (void)selectScheduleView
{
    [[self model] selectPaneType:MGPaneTypeSchedule];
}

- (void)selectBudgetView
{
    [[self model] selectPaneType:MGPaneTypeBudget];
}

- (void)selectCashculatorView
{
    [[self model] selectPaneType:MGPaneTypeCashculator];
}

- (void)selectGeneralLedgerView
{
    [[self model] selectPaneType:MGPaneTypeGeneralLedger];
}

- (void)selectDocPropsView
{
    [[self model] selectPaneType:MGPaneTypeDocProps];
}

- (void)selectPluginView
{
    [[self model] openSelectedPlugin];
}
@end