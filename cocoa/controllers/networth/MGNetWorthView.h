/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyNetWorthView.h"
#import "MGBaseView.h"
#import "HSOutlineView.h"
#import "MGBalanceSheet.h"
#import "MGPieChart.h"
#import "MGBalanceGraph.h"
#import "MGDoubleView.h"

@interface MGNetWorthView : MGBaseView
{
    IBOutlet HSOutlineView *outlineView;
    IBOutlet NSScrollView *outlineScrollView;
    IBOutlet MGDoubleView *pieChartsView;
    IBOutlet NSView *netWorthGraphPlaceholder;
    
    MGBalanceSheet *balanceSheet;
    MGPieChart *assetsPieChart;
    MGPieChart *liabilitiesPieChart;
    MGBalanceGraph *netWorthGraph;
}
- (id)initWithPy:(id)aPy;
- (PyNetWorthView *)model;

/* Public */
- (BOOL)canShowSelectedAccount;
- (void)toggleExcluded;

/* model --> view */
- (void)updateVisibility;
@end