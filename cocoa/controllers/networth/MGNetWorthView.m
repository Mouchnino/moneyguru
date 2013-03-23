/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGNetWorthView.h"
#import "MGAccountSheetView_UI.h"
#import "MGBalancePrint.h"
#import "MGConst.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGNetWorthView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithPyRef:aPyRef];
    self.view = createMGAccountSheetView_UI(self);
    balanceSheet = [[MGBalanceSheet alloc] initWithPyRef:[[self model] sheet] view:outlineView];
    pieChart = [[MGChart alloc] initWithPyRef:[[self model] pie] view:pieChartsView];
    graph = [[MGBalanceGraph alloc] initWithPyRef:[[self model] graph]];
    graphView = [graph view];
    [graphView setFrame:NSMakeRect(0, 0, 1, 258)];
    [self.view addSubview:graphView];
    [(NSSplitView *)self.view adjustSubviews];
    [(NSSplitView *)self.view setDelegate:self];
    [subSplitView setDelegate:self];
    return self;
}
        
- (void)dealloc
{
    [balanceSheet release];
    [graph release];
    [pieChart release];
    [super dealloc];
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