/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

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

/* This base class is to share the pie/graph visibility logic between netwroth and profit views
*/
@interface MGAccountSheetView : MGBaseView <NSSplitViewDelegate>
{
    /* Set these two in IB */
    IBOutlet NSSplitView *mainSplitView;
    IBOutlet NSSplitView *subSplitView;
    /* Set these two during initialization */
    NSView *graphView;
    NSView *pieView;
    
    BOOL graphCollapsed;
    BOOL pieCollapsed;
    CGFloat graphCollapseHeight;
    CGFloat pieCollapseWidth;
}
/* model --> view */
- (void)updateVisibility;
@end