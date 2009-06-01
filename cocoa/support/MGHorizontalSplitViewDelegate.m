#import "MGHorizontalSplitViewDelegate.h"

@implementation MGHorizontalSplitViewDelegate
- (float)splitView:(NSSplitView *)sender constrainMaxCoordinate:(float)proposedMax ofSubviewAt:(int)offset
{
    return proposedMax - 150.0;
}

- (float)splitView:(NSSplitView *)sender constrainMinCoordinate:(float)proposedMin ofSubviewAt:(int)offset
{
    return proposedMin + 100.0;
}

- (BOOL)splitView:(NSSplitView *)sender canCollapseSubview:(NSView *)subview
{
    return (subview == graphView);
}

@end