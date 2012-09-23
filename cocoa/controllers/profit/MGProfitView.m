/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGProfitView.h"
#import "MGAccountSheetView_UI.h"
#import "MGProfitPrint.h"
#import "MGConst.h"
#import "HSPyUtil.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGProfitView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyProfitView *m = [[PyProfitView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"ViewWithGraphView", self)];
    [m release];
    self.wholeView = createMGAccountSheetView_UI(self);
    incomeStatement = [[MGIncomeStatement alloc] initWithPyRef:[[self model] sheet] view:outlineView];
    pieChart = [[MGChart alloc] initWithPyRef:[[self model] pie] view:pieChartsView];
    profitGraph = [[MGBarGraph alloc] initWithPyRef:[[self model] pgraph]];
    graphView = [profitGraph view];
    [graphView setFrame:NSMakeRect(0, 0, 1, 258)];
    [wholeView addSubview:graphView];
    [(NSSplitView *)wholeView adjustSubviews];
    [(NSSplitView *)wholeView setDelegate:self];
    [subSplitView setDelegate:self];
    return self;
}
        
- (void)dealloc
{
    [incomeStatement release];
    [profitGraph release];
    [pieChartsView release];
    [super dealloc];
}

- (PyProfitView *)model
{
    return (PyProfitView *)model;
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : [profitGraph view];
    MGPieChartView *printPieChartView = [hiddenAreas containsIndex:MGPaneAreaRightChart] ? nil : pieChartsView;
    MGProfitPrint *p = [[MGProfitPrint alloc] initWithPyParent:[self model] outlineView:outlineView
        graphView:printGraphView pieView:printPieChartView];
    return [p autorelease];
}

- (NSString *)tabIconName
{
    return @"income_statement_16";
}

/* Public */
- (BOOL)canShowSelectedAccount
{
    return [incomeStatement canShowSelectedAccount];
}

- (void)toggleExcluded
{
    [[incomeStatement model] toggleExcluded];
}
@end