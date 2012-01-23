/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyProfitView.h"
#import "MGBaseView.h"
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
    
    MGIncomeStatement *incomeStatement;
    MGPieChart *incomePieChart;
    MGPieChart *expensesPieChart;
    MGBarGraph *profitGraph;
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyProfitView *)model;

/* Public */
- (BOOL)canShowSelectedAccount;
- (void)toggleExcluded;

/* model --> view */
- (void)updateVisibility;
@end