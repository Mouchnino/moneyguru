/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGDocument.h"
#import "MGReport.h"
#import "MGPieChart.h"
#import "MGBalanceGraph.h"
#import "MGDoubleView.h"
#import "PyBalanceSheet.h"

@interface MGBalanceSheet : MGReport
{
    IBOutlet NSView *mainView;
    IBOutlet MGDoubleView *pieChartsView;
    IBOutlet NSView *netWorthGraphPlaceholder;
    
    HSTableColumnManager *columnsManager;
    MGPieChart *assetsPieChart;
    MGPieChart *liabilitiesPieChart;
    MGBalanceGraph *netWorthGraph;
}
- (id)initWithDocument:(MGDocument *)document;
- (PyBalanceSheet *)py;

/* Private */
- (void)updateVisibility;
@end