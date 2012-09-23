/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGNetWorthView.h"
#import "MGAccountSheetView_UI.h"
#import "MGBalancePrint.h"
#import "MGConst.h"
#import "HSPyUtil.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGNetWorthView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyNetWorthView *m = [[PyNetWorthView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"ViewWithGraphView", self)];
    [m release];
    self.wholeView = createMGAccountSheetView_UI(self);
    balanceSheet = [[MGBalanceSheet alloc] initWithPyRef:[[self model] sheet] view:outlineView];
    pieChart = [[MGChart alloc] initWithPyRef:[[self model] pie] view:pieChartsView];
    netWorthGraph = [[MGBalanceGraph alloc] initWithPyRef:[[self model] nwgraph]];
    graphView = [netWorthGraph view];
    [graphView setFrame:NSMakeRect(0, 0, 1, 258)];
    [wholeView addSubview:graphView];
    [(NSSplitView *)wholeView adjustSubviews];
    [(NSSplitView *)wholeView setDelegate:self];
    [subSplitView setDelegate:self];
    return self;
}
        
- (void)dealloc
{
    [balanceSheet release];
    [netWorthGraph release];
    [pieChart release];
    [super dealloc];
}

- (PyNetWorthView *)model
{
    return (PyNetWorthView *)model;
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : graphView;
    MGPieChartView *printPieChartView = [hiddenAreas containsIndex:MGPaneAreaRightChart] ? nil : pieChartsView;
    MGBalancePrint *p = [[MGBalancePrint alloc] initWithPyParent:[self model] outlineView:outlineView
        graphView:printGraphView pieView:printPieChartView];
    return [p autorelease];
}

- (NSString *)tabIconName
{
    return @"balance_sheet_16";
}

/* Public */
- (BOOL)canShowSelectedAccount
{
    return [balanceSheet canShowSelectedAccount];
}

- (void)toggleExcluded
{
    [[balanceSheet model] toggleExcluded];
}

@end