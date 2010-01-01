/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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