/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGNetWorthView.h"
#import "MGBalancePrint.h"
#import "MGConst.h"
#import "Utils.h"
#import "PyMainWindow.h"

@implementation MGNetWorthView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyNetWorthView *m = [[PyNetWorthView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"ViewWithGraphView", self)];
    [m release];
    [NSBundle loadNibNamed:@"BalanceSheet" owner:self];
    balanceSheet = [[MGBalanceSheet alloc] initWithPyRef:[[self model] sheet] view:outlineView];
    assetsPieChart = [[MGPieChart alloc] initWithPyRef:[[self model] apie]];
    liabilitiesPieChart = [[MGPieChart alloc] initWithPyRef:[[self model] lpie]];
    [pieChartsView setFirstView:[assetsPieChart view]];
    [pieChartsView setSecondView:[liabilitiesPieChart view]];
    netWorthGraph = [[MGBalanceGraph alloc] initWithPyRef:[[self model] nwgraph]];
    NSView *graphView = [netWorthGraph view];
    [graphView setFrame:[netWorthGraphPlaceholder frame]];
    [graphView setAutoresizingMask:[netWorthGraphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:netWorthGraphPlaceholder with:graphView];
    return self;
}
        
- (void)dealloc
{
    [balanceSheet release];
    [netWorthGraph release];
    [assetsPieChart release];
    [liabilitiesPieChart release];
    [super dealloc];
}

- (PyNetWorthView *)model
{
    return (PyNetWorthView *)model;
}

- (MGPrintView *)viewToPrint
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    NSView *printGraphView = [hiddenAreas containsIndex:MGPaneAreaBottomGraph] ? nil : [netWorthGraph view];
    MGDoubleView *printPieChartView = [hiddenAreas containsIndex:MGPaneAreaRightChart] ? nil : pieChartsView;
    MGBalancePrint *p = [[MGBalancePrint alloc] initWithPyParent:[self model] outlineView:outlineView
        graphView:printGraphView pieViews:printPieChartView];
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

/* model --> view */
- (void)updateVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    BOOL graphVisible = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    BOOL pieVisible = ![hiddenAreas containsIndex:MGPaneAreaRightChart];
    // Let's set initial rects
    NSRect mainRect = [outlineScrollView frame];
    NSRect pieRect = [pieChartsView frame];
    NSRect graphRect = [[netWorthGraph view] frame];
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
    [[netWorthGraph view] setHidden:!graphVisible];
    [outlineScrollView setFrame:mainRect];
    [pieChartsView setFrame:pieRect];
}
@end