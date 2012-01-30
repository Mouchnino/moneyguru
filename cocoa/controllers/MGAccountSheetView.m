/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountSheetView.h"
#import "MGConst.h"
#import "Utils.h"

@implementation MGAccountSheetView
/* Delegate */

- (CGFloat)splitView:(NSSplitView *)splitView constrainMinCoordinate:(CGFloat)proposedMin ofSubviewAt:(NSInteger)dividerIndex
{
    if (splitView == mainSplitView) {
        return 200;
    }
    else if (splitView == subSplitView) {
        return 100;
    }
    return proposedMin;
}

- (CGFloat)splitView:(NSSplitView *)splitView constrainMaxCoordinate:(CGFloat)proposedMax ofSubviewAt:(NSInteger)dividerIndex
{
    if (splitView == mainSplitView) {
        return NSHeight([splitView frame]) - 130;
    }
    else if (splitView == subSplitView) {
        return NSWidth([splitView frame]) - 170;
    }
    return proposedMax;
}

- (BOOL)splitView:(NSSplitView *)splitView canCollapseSubview:(NSView *)subview
{
    if (subview == pieView) {
        return pieCollapsed;
    }
    if (subview == graphView) {
        return graphCollapsed;
    }
    return NO;
}

/* model --> view */
- (void)updateVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    BOOL graphVisible = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    BOOL pieVisible = ![hiddenAreas containsIndex:MGPaneAreaRightChart];
    if (graphVisible) {
        if (graphCollapsed) {
            graphCollapsed = NO;
            CGFloat pos = NSHeight([mainSplitView frame])- graphCollapseHeight - [mainSplitView dividerThickness];
            [mainSplitView setPosition:pos ofDividerAtIndex:0];
        }
    }
    else {
        if (!graphCollapsed) {
            graphCollapsed = YES;
            graphCollapseHeight = NSHeight([graphView frame]);
            [mainSplitView setPosition:NSHeight([mainSplitView frame]) ofDividerAtIndex:0];
        }
    }
    if (pieVisible) {
        if (pieCollapsed) {
            pieCollapsed = NO;
            CGFloat pos = NSWidth([subSplitView frame])- pieCollapseWidth - [subSplitView dividerThickness];
            [subSplitView setPosition:pos ofDividerAtIndex:0];
        }
    }
    else {
        if (!pieCollapsed) {
            pieCollapsed = YES;
            pieCollapseWidth = NSWidth([pieView frame]);
            [subSplitView setPosition:NSWidth([subSplitView frame]) ofDividerAtIndex:0];
        }
    }
}
@end