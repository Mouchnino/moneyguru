/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGLineGraphView.h"
#import "MGUtils.h"

@implementation MGLineGraphView
- (void)drawGraph
{
    if ([data count] <= 1)
        return;
    float xTodayFactored = xToday * xFactor;
    NSEnumerator *dataEnumerator = [data objectEnumerator];
    NSArray *dataPoint = [dataEnumerator nextObject];
    NSPoint point = NSMakePoint([[dataPoint objectAtIndex:0] floatValue] * xFactor, [[dataPoint objectAtIndex:1] floatValue] * yFactor);
    float firstX = point.x;
    NSBezierPath *dataPath = [NSBezierPath bezierPath];
    NSBezierPath *dataFillPath = [NSBezierPath bezierPath];
    [dataPath moveToPoint:point];
    [dataFillPath moveToPoint:NSMakePoint(point.x, 0)];
    [dataFillPath lineToPoint:point];
    while (dataPoint = [dataEnumerator nextObject])
    {
        point = NSMakePoint([[dataPoint objectAtIndex:0] floatValue] * xFactor, [[dataPoint objectAtIndex:1] floatValue] * yFactor);
        [dataPath lineToPoint:point];
        [dataFillPath lineToPoint:point];
    }
    float lastX = point.x;
    [dataFillPath lineToPoint:NSMakePoint(point.x, 0)];
    [NSGraphicsContext saveGraphicsState];
    [dataFillPath addClip];
    [self fillRect:graphBounds withGradient:fillGradient];
    if ((xTodayFactored <= lastX) && (xTodayFactored < NSMaxX(graphBounds)))
    {
        NSRect futureBounds = NSMakeRect(xTodayFactored, graphBounds.origin.y, NSMaxX(graphBounds) - xTodayFactored, graphBounds.size.height);
        [self fillRect:futureBounds withGradient:futureGradient];
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
    [dataPath setLineWidth:GRAPH_LINE_WIDTH];
    [[NSColor colorWithDeviceRed:0.078 green:0.62 blue:0.043 alpha:1.0] setStroke];
    [dataPath stroke];
}

@end
