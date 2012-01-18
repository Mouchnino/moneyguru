/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGProfitView.h"
#import "MGProfitPrint.h"
#import "MGConst.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGProfitView
- (id)initWithPy:(id)aPy
{
    self = [super initWithPy:aPy];
    [NSBundle loadNibNamed:@"IncomeStatement" owner:self];
    incomeStatement = [[MGIncomeStatement alloc] initWithPy:[[self py] sheet] view:outlineView];
    incomePieChart = [[MGPieChart alloc] initWithPy:[[self py] ipie]];
    expensesPieChart = [[MGPieChart alloc] initWithPy:[[self py] epie]];
    [pieChartsView setFirstView:[incomePieChart view]];
    [pieChartsView setSecondView:[expensesPieChart view]];
    profitGraph = [[MGBarGraph alloc] initWithPy:[[self py] pgraph]];
    NSView *graphView = [profitGraph view];
    [graphView setFrame:[profitGraphPlaceholder frame]];
    [graphView setAutoresizingMask:[profitGraphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:profitGraphPlaceholder with:graphView];
    return self;
}
        
- (void)dealloc
{
    [incomeStatement release];
    [profitGraph release];
    [incomePieChart release];
    [expensesPieChart release];
    [super dealloc];
}

- (PyProfitView *)py
{
    return (PyProfitView *)py;
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[[self py] mainwindow] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : [profitGraph view];
    MGDoubleView *printPieChartView = [hiddenAreas containsIndex:MGPaneAreaRightChart] ? nil : pieChartsView;
    MGProfitPrint *p = [[MGProfitPrint alloc] initWithPyParent:[self py] outlineView:outlineView
        graphView:printGraphView pieViews:printPieChartView];
    return [p autorelease];
}

/* Public */
- (BOOL)canShowSelectedAccount
{
    return [incomeStatement canShowSelectedAccount];
}

- (void)toggleExcluded
{
    [[incomeStatement py] toggleExcluded];
}

/* model --> view */
- (void)updateVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[[self py] mainwindow] hiddenAreas]];
    BOOL graphVisible = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    BOOL pieVisible = ![hiddenAreas containsIndex:MGPaneAreaRightChart];
    // Let's set initial rects
    NSRect mainRect = [outlineScrollView frame];
    NSRect pieRect = [pieChartsView frame];
    NSRect graphRect = [[profitGraph view] frame];
    if (graphVisible) {
        pieRect.size.height = NSMaxY(pieRect) - NSMaxY(graphRect);
        pieRect.origin.y = NSMaxY(graphRect);
        mainRect.size.height = NSMaxY(mainRect) - NSMaxY(graphRect);
        mainRect.origin.y = NSMaxY(graphRect);
    }
    else {
        pieRect.size.height = NSMaxY(pieRect) - NSMinY(graphRect);
        pieRect.origin.y = NSMinY(graphRect);
        mainRect.size.height = NSMaxY(mainRect) - NSMinY(graphRect);
        mainRect.origin.y = NSMinY(graphRect);
    }
    if (pieVisible) {
        mainRect.size.width = NSMinX(mainRect) + NSMinX(pieRect);
    }
    else {
        mainRect.size.width = NSMinX(mainRect) + NSMaxX(pieRect);
    }
    [pieChartsView setHidden:!pieVisible];
    [[profitGraph view] setHidden:!graphVisible];
    [outlineScrollView setFrame:mainRect];
    [pieChartsView setFrame:pieRect];
}
@end