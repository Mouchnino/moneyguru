/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGProfitView.h"
#import "MGProfitPrint.h"
#import "MGConst.h"
#import "Utils.h"

@implementation MGProfitView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyProfitView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"IncomeStatement" owner:self];
    incomeStatement = [[MGIncomeStatement alloc] initWithPyParent:[self py] view:outlineView];
    incomePieChart = [[MGPieChart alloc] initWithPyParent:[self py] pieChartClassName:@"PyIncomePieChart"];
    expensesPieChart = [[MGPieChart alloc] initWithPyParent:[self py] pieChartClassName:@"PyExpensesPieChart"];
    [pieChartsView setFirstView:[incomePieChart view]];
    [pieChartsView setSecondView:[expensesPieChart view]];
    profitGraph = [[MGBarGraph alloc] initWithPyParent:[self py] pyClassName:@"PyProfitGraph"];
    NSView *graphView = [profitGraph view];
    [graphView setFrame:[profitGraphPlaceholder frame]];
    [graphView setAutoresizingMask:[profitGraphPlaceholder autoresizingMask]];
    [wholeView replaceSubview:profitGraphPlaceholder with:graphView];
    
    NSArray *children = [NSArray arrayWithObjects:[incomeStatement py], [profitGraph py],
        [incomePieChart py], [expensesPieChart py], nil];
    [[self py] setChildren:children];
    
    [self updateVisibility];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud addObserver:self forKeyPath:ProfitGraphVisible options:NSKeyValueObservingOptionNew context:NULL];
    [ud addObserver:self forKeyPath:IncomeExpensePieChartVisible options:NSKeyValueObservingOptionNew context:NULL];
    return self;
}
        
- (void)dealloc
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud removeObserver:self forKeyPath:ProfitGraphVisible];
    [ud removeObserver:self forKeyPath:IncomeExpensePieChartVisible];
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
    MGProfitPrint *p = [[MGProfitPrint alloc] initWithPyParent:[self py] outlineView:outlineView
        graphView:[profitGraph view] pieViews:pieChartsView];
    return [p autorelease];
}

/* Private */
- (void)updateVisibility
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    BOOL graphVisible = [ud boolForKey:ProfitGraphVisible];
    BOOL pieVisible = [ud boolForKey:IncomeExpensePieChartVisible];
    // Let's set initial rects
    NSRect mainRect = [outlineScrollView frame];
    NSRect pieRect = [pieChartsView frame];
    NSRect graphRect = [[profitGraph view] frame];
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
    [[profitGraph view] setHidden:!graphVisible];
    [outlineScrollView setFrame:mainRect];
    [pieChartsView setFrame:pieRect];
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

/* Delegate */
- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    [self updateVisibility];
}
@end