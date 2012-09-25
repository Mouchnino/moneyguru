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
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGProfitView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    self = [super initWithPyRef:aPyRef];
    self.view = createMGAccountSheetView_UI(self);
    incomeStatement = [[MGIncomeStatement alloc] initWithPyRef:[[self model] sheet] view:outlineView];
    pieChart = [[MGChart alloc] initWithPyRef:[[self model] pie] view:pieChartsView];
    graph = [[MGBarGraph alloc] initWithPyRef:[[self model] graph]];
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
    [incomeStatement release];
    [graph release];
    [pieChartsView release];
    [super dealloc];
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : graphView;
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