/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyNetWorthView.h"
#import "MGAccountSheetView.h"
#import "HSOutlineView.h"
#import "MGBalanceSheet.h"
#import "MGPieChart.h"
#import "MGBalanceGraph.h"
#import "MGDoubleView.h"

@interface MGNetWorthView : MGAccountSheetView
{
    IBOutlet HSOutlineView *outlineView;
    IBOutlet MGDoubleView *pieChartsView;
    
    MGBalanceSheet *balanceSheet;
    MGPieChart *assetsPieChart;
    MGPieChart *liabilitiesPieChart;
    MGBalanceGraph *netWorthGraph;
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyNetWorthView *)model;

/* Public */
- (BOOL)canShowSelectedAccount;
- (void)toggleExcluded;
@end