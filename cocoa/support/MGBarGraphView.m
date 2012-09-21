/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBarGraphView.h"

// Synced with core
#define MGPenIDAxis 1
#define MGPenIDBar 2
#define MGPenIDTodayLine 3

#define MGBrushIDNormalBar 1
#define MGBrushIDFutureBar 2

@implementation MGBarGraphView
- (MGPen *)penForID:(NSInteger)aPenID
{
    if (aPenID == MGPenIDBar) {
        return [MGPen penWithColor:[NSColor colorWithDeviceRed:0.078 green:0.62 blue:0.043 alpha:1.0] width:GRAPH_LINE_WIDTH];
    }
    else if (aPenID == MGPenIDTodayLine) {
        return [MGPen penWithColor:[NSColor redColor] width:GRAPH_LINE_WIDTH];
    }
    else {
        return nil;
    }
}

- (MGBrush *)brushForID:(NSInteger)aBrushID
{
    if (aBrushID == MGBrushIDNormalBar) {
        NSColor *darkGreen = [NSColor colorWithDeviceRed:0.365 green:0.737 blue:0.337 alpha:1.0];
        return [MGBrush brushWithColor:darkGreen isGradient:YES];
    }
    else if (aBrushID == MGBrushIDFutureBar) {
        return [MGBrush brushWithColor:[NSColor lightGrayColor] isGradient:YES];
    }
    else {
        return nil;
    }
}
- (void)drawGraph
{
    [self.model drawWithXFactor:xFactor yFactor:yFactor];
    [self drawAxisOverlayY];
    /* We don't draw the X overlay in a bar graph */
}

@end
