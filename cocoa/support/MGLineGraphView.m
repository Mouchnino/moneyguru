/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGLineGraphView.h"
#import "Utils.h"

@implementation MGLineGraphView
- (void)drawGraph
{
    if ([data count] <= 1)
        return;
    CGFloat xTodayFactored = xToday * xFactor;
    NSEnumerator *dataEnumerator = [data objectEnumerator];
    NSArray *dataPoint = [dataEnumerator nextObject];
    NSPoint point = NSMakePoint(n2f([dataPoint objectAtIndex:0]) * xFactor, n2f([dataPoint objectAtIndex:1]) * yFactor);
    CGFloat firstX = point.x;
    NSBezierPath *dataPath = [NSBezierPath bezierPath];
    NSBezierPath *dataFillPath = [NSBezierPath bezierPath];
    [dataPath moveToPoint:point];
    [dataFillPath moveToPoint:NSMakePoint(point.x, 0)];
    [dataFillPath lineToPoint:point];
    while (dataPoint = [dataEnumerator nextObject])
    {
        point = NSMakePoint(n2f([dataPoint objectAtIndex:0]) * xFactor, n2f([dataPoint objectAtIndex:1]) * yFactor);
        [dataPath lineToPoint:point];
        [dataFillPath lineToPoint:point];
    }
    CGFloat lastX = point.x;
    [dataFillPath lineToPoint:NSMakePoint(point.x, 0)];
    [NSGraphicsContext saveGraphicsState];
    [dataFillPath addClip];
    [fillGradient drawInRect:graphBounds angle:90];
    if ((xTodayFactored <= lastX) && (xTodayFactored < NSMaxX(graphBounds)))
    {
        NSRect futureBounds = NSMakeRect(xTodayFactored, graphBounds.origin.y, NSMaxX(graphBounds) - xTodayFactored, graphBounds.size.height);
        [futureGradient drawInRect:futureBounds angle:90];
    }    
    if ((xTodayFactored >= firstX) && (xTodayFactored <= lastX))
    {
        NSBezierPath *redLine = [NSBezierPath bezierPath];
        [redLine moveToPoint:NSMakePoint(xTodayFactored, NSMinY(graphBounds))];
        [redLine lineToPoint:NSMakePoint(xTodayFactored, NSMaxY(graphBounds))];
        [redLine setLineWidth:GRAPH_LINE_WIDTH];
        [[NSColor redColor] setStroke];
        [redLine stroke];
    }
    [NSGraphicsContext restoreGraphicsState];
    /* It looks better if we draw axis overlay before we draw our main line */
    [self drawAxisOverlayX];
    [self drawAxisOverlayY];
    [dataPath setLineWidth:GRAPH_LINE_WIDTH];
    [[NSColor colorWithDeviceRed:0.078 green:0.62 blue:0.043 alpha:1.0] setStroke];
    [dataPath stroke];
}

@end
