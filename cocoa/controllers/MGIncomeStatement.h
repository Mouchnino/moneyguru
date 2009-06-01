#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGDocument.h"
#import "MGReport.h"
#import "MGPieChart.h"
#import "MGBarGraph.h"
#import "MGDoubleView.h"
#import "PyIncomeStatement.h"

@interface MGIncomeStatement : MGReport
{
    IBOutlet NSView *mainView;
    IBOutlet MGDoubleView *pieChartsView;
    IBOutlet NSView *profitGraphPlaceholder;
    
    HSTableColumnManager *columnsManager;
    MGPieChart *incomePieChart;
    MGPieChart *expensesPieChart;
    MGBarGraph *profitGraph;
}
- (id)initWithDocument:(MGDocument *)document;
- (PyIncomeStatement *)py;

/* Private */
- (void)updateVisibility;
@end