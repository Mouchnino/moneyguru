/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyAccountSheetView.h"
#import "MGBaseView.h"
#import "HSOutlineView.h"
#import "MGBalanceSheet.h"
#import "MGBalanceGraph.h"
#import "MGPieChartView.h"
#import "MGChart.h"

/* This base class is to share the pie/graph visibility logic between netwroth and profit views
*/
@interface MGAccountSheetView : MGBaseView <NSSplitViewDelegate>
{
    NSSplitView *mainSplitView;
    NSSplitView *subSplitView;
    HSOutlineView *outlineView;
    MGPieChartView *pieChartsView;
    
    /* Set this during initialization */
    NSView *graphView;
    MGChart *pieChart;
    MGChart *graph;
    
    BOOL graphCollapsed;
    BOOL pieCollapsed;
    CGFloat graphCollapseHeight;
    CGFloat pieCollapseWidth;
}

@property (readwrite, retain) NSSplitView *mainSplitView;
@property (readwrite, retain) NSSplitView *subSplitView;
@property (readwrite, retain) HSOutlineView *outlineView;
@property (readwrite, retain) MGPieChartView *pieChartsView;

- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyAccountSheetView *)model;
@end