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