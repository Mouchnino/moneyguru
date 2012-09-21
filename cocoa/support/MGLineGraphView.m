/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGLineGraphView.h"
#import "Utils.h"

// Synced with core
#define MGPenIDGraph 3
#define MGPenIDTodayLine 4

#define MGBrushIDGraphNormal 1
#define MGBrushIDGraphFuture 2

@implementation MGLineGraphView
- (MGPen *)penForID:(NSInteger)aPenID
{
    if (aPenID == MGPenIDGraph) {
        return [MGPen penWithColor:[NSColor colorWithDeviceRed:0.078 green:0.62 blue:0.043 alpha:1.0] width:GRAPH_LINE_WIDTH];
    }
    else if (aPenID == MGPenIDTodayLine) {
        return [MGPen penWithColor:[NSColor redColor] width:GRAPH_LINE_WIDTH];
    }
    else {
        return [super penForID:aPenID];
    }
}

- (MGBrush *)brushForID:(NSInteger)aBrushID
{
    if (aBrushID == MGBrushIDGraphNormal) {
        NSColor *darkGreen = [NSColor colorWithDeviceRed:0.365 green:0.737 blue:0.337 alpha:1.0];
        return [MGBrush brushWithColor:darkGreen isGradient:YES];
    }
    else if (aBrushID == MGBrushIDGraphFuture) {
        return [MGBrush brushWithColor:[NSColor lightGrayColor] isGradient:YES];
    }
    else {
        return [super brushForID:aBrushID];
    }
}
@end
