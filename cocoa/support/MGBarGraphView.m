/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBarGraphView.h"

@implementation MGBarGraphView
- (void)drawGraph
{
    for (NSArray *dataPoint in data) {
        CGFloat x1 = [[dataPoint objectAtIndex:0] floatValue] * xFactor;
        CGFloat x2 = [[dataPoint objectAtIndex:1] floatValue] * xFactor;
        CGFloat h1 = [[dataPoint objectAtIndex:2] floatValue] * yFactor;
        CGFloat h2 = [[dataPoint objectAtIndex:3] floatValue] * yFactor;
        CGFloat lowH = 0;
        CGFloat highH = 0;
        BOOL showRedLine = (h1 != 0) && (h2 != 0);
        CGFloat redLineY = 0;
        NSRect pastRect = NSMakeRect(x1, 0.0, x2-x1, ABS(h1));
        NSRect futureRect = NSMakeRect(x1, 0.0, x2-x1, ABS(h2));
        if (h1 >= 0)
        {
            highH = h1;
        }
        else
        {
            pastRect.origin.y = h1;
            lowH = h1;
        }
        if (h2 >= 0)
        {
            redLineY = highH;
            futureRect.origin.y = highH;
            highH += h2;
        }
        else
        {
            redLineY = lowH;
            lowH += h2;
            futureRect.origin.y = lowH;
        }
        [NSGraphicsContext saveGraphicsState];
        [NSBezierPath clipRect:pastRect];
        [fillGradient drawInRect:graphBounds angle:90];
        [NSGraphicsContext restoreGraphicsState];
        [NSGraphicsContext saveGraphicsState];
        [NSBezierPath clipRect:futureRect];
        [futureGradient drawInRect:graphBounds angle:90];
        [NSGraphicsContext restoreGraphicsState];
        if (showRedLine)
        {
            NSBezierPath *redLine = [NSBezierPath bezierPath];
            [redLine moveToPoint:NSMakePoint(x1, redLineY)];
            [redLine lineToPoint:NSMakePoint(x2, redLineY)];
            [redLine setLineWidth:GRAPH_LINE_WIDTH];
            [[NSColor redColor] setStroke];
            [redLine stroke];
        }
        NSBezierPath *path = [NSBezierPath bezierPath];
        [path setLineWidth:GRAPH_LINE_WIDTH];
        [path moveToPoint:NSMakePoint(x1, lowH)];
        [path lineToPoint:NSMakePoint(x1, highH)];
        if (highH != 0)
            [path lineToPoint:NSMakePoint(x2, highH)];
        else
            [path moveToPoint:NSMakePoint(x2, highH)];
        [path lineToPoint:NSMakePoint(x2, lowH)];
        if (lowH != 0)
            [path lineToPoint:NSMakePoint(x1, lowH)];
        [[NSColor colorWithDeviceRed:0.078 green:0.62 blue:0.043 alpha:1.0] setStroke];
        [path stroke];
    }
    [self drawAxisOverlayY];
    /* We don't draw the X overlay in a bar graph */
}

@end
