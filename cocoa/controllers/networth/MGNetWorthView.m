/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

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
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyNetWorthView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"BalanceSheet" owner:self];
    balanceSheet = [[MGBalanceSheet alloc] initWithPyParent:[self py] view:outlineView];
    assetsPieChart = [[MGPieChart alloc] initWithPyParent:[self py] pieChartClassName:@"PyAssetsPieChart"];
    liabilitiesPieChart = [[MGPieChart alloc] initWithPyParent:[self py] pieChartClassName:@"PyLiabilitiesPieChart"];
    [pieChartsView setFirstView:[assetsPieChart view]];
    [pieChartsView setSecondView:[liabilitiesPieChart view]];
    netWorthGraph = [[MGBalanceGraph alloc] initWithPyParent:[self py] pyClassName:@"PyNetWorthGraph"];
    NSView *graphView = [netWorthGraph view];
    [graphView setFrame:[netWorthGraphPlaceholder frame]];
    [graphView setAutoresizingMask:[netWorthGraphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:netWorthGraphPlaceholder with:graphView];
    
    NSArray *children = [NSArray arrayWithObjects:[balanceSheet py], [netWorthGraph py],
        [assetsPieChart py], [liabilitiesPieChart py], nil];
    [[self py] setChildren:children];
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

- (PyNetWorthView *)py
{
    return (PyNetWorthView *)py;
}

- (MGPrintView *)viewToPrint
{
    MGBalancePrint *p = [[MGBalancePrint alloc] initWithPyParent:[self py] outlineView:outlineView
        graphView:[netWorthGraph view] pieViews:pieChartsView];
    return [p autorelease];
}

/* Public */
- (BOOL)canShowSelectedAccount
{
    return [balanceSheet canShowSelectedAccount];
}

- (void)toggleExcluded
{
    [[balanceSheet py] toggleExcluded];
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