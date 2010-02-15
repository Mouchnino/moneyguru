/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyProfitView.h"
#import "MGBaseView.h"
#import "MGDocument.h"
#import "HSOutlineView.h"
#import "MGIncomeStatement.h"
#import "MGPieChart.h"
#import "MGBarGraph.h"
#import "MGDoubleView.h"

@interface MGProfitView : MGBaseView
{
    IBOutlet HSOutlineView *outlineView;
    IBOutlet NSScrollView *outlineScrollView;
    IBOutlet MGDoubleView *pieChartsView;
    IBOutlet NSView *profitGraphPlaceholder;
    
    PyProfitView *py;
    MGIncomeStatement *incomeStatement;
    MGPieChart *incomePieChart;
    MGPieChart *expensesPieChart;
    MGBarGraph *profitGraph;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyProfitView *)py;

/* Private */
- (void)updateVisibility;

/* Public */
- (BOOL)canShowSelectedAccount;
@end