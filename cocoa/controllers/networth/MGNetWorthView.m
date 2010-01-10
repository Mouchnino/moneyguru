/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGNetWorthView.h"
#import "MGBalancePrint.h"
#import "MGConst.h"
#import "MGUtils.h"

@implementation MGNetWorthView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"BalanceSheet" owner:self];
    balanceSheet = [[MGBalanceSheet alloc] initWithDocument:aDocument view:outlineView];
    assetsPieChart = [[MGPieChart alloc] initWithDocument:aDocument pieChartClassName:@"PyAssetsPieChart"];
    liabilitiesPieChart = [[MGPieChart alloc] initWithDocument:aDocument pieChartClassName:@"PyLiabilitiesPieChart"];
    [pieChartsView setFirstView:[assetsPieChart view]];
    [pieChartsView setSecondView:[liabilitiesPieChart view]];
    netWorthGraph = [[MGBalanceGraph alloc] initWithDocument:aDocument pyClassName:@"PyNetWorthGraph"];
    NSView *graphView = [netWorthGraph view];
    [graphView setFrame:[netWorthGraphPlaceholder frame]];
    [graphView setAutoresizingMask:[netWorthGraphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:netWorthGraphPlaceholder with:graphView];
    
    NSArray *children = [NSArray arrayWithObjects:[balanceSheet py], [netWorthGraph py],
        [assetsPieChart py], [liabilitiesPieChart py], nil];
    Class pyClass = [MGUtils classNamed:@"PyNetWorthView"];
    py = [[pyClass alloc] initWithCocoa:self pyParent:[aDocument py] children:children];
    
    [self updateVisibility];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud addObserver:self forKeyPath:AssetLiabilityPieChartVisible options:NSKeyValueObservingOptionNew context:NULL];
    [ud addObserver:self forKeyPath:NetWorthGraphVisible options:NSKeyValueObservingOptionNew context:NULL];
    return self;
}
        
- (void)dealloc
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud removeObserver:self forKeyPath:AssetLiabilityPieChartVisible];
    [ud removeObserver:self forKeyPath:NetWorthGraphVisible];
    [balanceSheet release];
    [netWorthGraph release];
    [assetsPieChart release];
    [liabilitiesPieChart release];
    [py release];
    [super dealloc];
}

- (oneway void)release
{
    if ([self retainCount] == 2)
        [py free];
    [super release];
}

- (PyNetWorthView *)py
{
    return (PyNetWorthView *)py;
}

- (MGPrintView *)viewToPrint
{
    MGBalancePrint *p = [[MGBalancePrint alloc] initWithPyParent:[balanceSheet py] outlineView:outlineView
        graphView:[netWorthGraph view] pieViews:pieChartsView];
    return [p autorelease];
}

/* Private */
- (void)updateVisibility
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    BOOL graphVisible = [ud boolForKey:NetWorthGraphVisible];
    BOOL pieVisible = [ud boolForKey:AssetLiabilityPieChartVisible];
    // Let's set initial rects
    NSRect mainRect = [outlineScrollView frame];
    NSRect pieRect = [pieChartsView frame];
    NSRect graphRect = [[netWorthGraph view] frame];
    if (graphVisible)
    {
        pieRect.size.height = NSMaxY(pieRect) - NSMaxY(graphRect);
        pieRect.origin.y = NSMaxY(graphRect);
        mainRect.size.height = NSMaxY(mainRect) - NSMaxY(graphRect);
        mainRect.origin.y = NSMaxY(graphRect);
    }
    else
    {
        pieRect.size.height = NSMaxY(pieRect) - NSMinY(graphRect);
        pieRect.origin.y = NSMinY(graphRect);
        mainRect.size.height = NSMaxY(mainRect) - NSMinY(graphRect);
        mainRect.origin.y = NSMinY(graphRect);
    }
    if (pieVisible)
    {
        mainRect.size.width = NSMinX(mainRect) + NSMinX(pieRect);
    }
    else
    {
        mainRect.size.width = NSMinX(mainRect) + NSMaxX(pieRect);
    }
    [pieChartsView setHidden:!pieVisible];
    [[netWorthGraph view] setHidden:!graphVisible];
    [outlineScrollView setFrame:mainRect];
    [pieChartsView setFrame:pieRect];
}

/* Delegate */
- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    [self updateVisibility];
}
@end