/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGraphView.h"
#import "Utils.h"

// Synced with core
#define MGFontIDTitle 1
#define MGFontIDAxisLabel 2

#define MGPenIDAxis 1
#define MGPenIDAxisOverlay 2

@implementation MGGraphView
- (id)init
{
    self = [super init];
    axisColor = [NSColor darkGrayColor];
    NSColor *darkGreen = [NSColor colorWithDeviceRed:0.365 green:0.737 blue:0.337 alpha:1.0];
    NSColor *lightGreen = [NSColor colorWithDeviceRed:0.643 green:0.847 blue:0.62 alpha:1.0];
    fillGradient = [[NSGradient alloc] initWithStartingColor:darkGreen endingColor:lightGreen];
    NSColor *darkGray = [NSColor lightGrayColor];
    NSColor *lightGray = [darkGray blendedColorWithFraction:0.5 ofColor:[NSColor whiteColor]];
    futureGradient = [[NSGradient alloc] initWithStartingColor:darkGray endingColor:lightGray];
    return self;
}

- (void)dealloc
{
    [fillGradient release];
    [futureGradient release];
    [super dealloc];
}

- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID
{
    NSMutableParagraphStyle *pstyle = [[[NSMutableParagraphStyle alloc] init] autorelease];
    [pstyle setAlignment:NSCenterTextAlignment];
    if (aFontID == MGFontIDTitle) {
        NSFont *titleFont = [NSFont boldSystemFontOfSize:GRAPH_TITLE_FONT_SIZE];
        return [NSDictionary dictionaryWithObjectsAndKeys:
            titleFont, NSFontAttributeName,
            titleColor, NSForegroundColorAttributeName,
            pstyle, NSParagraphStyleAttributeName,
            nil];
    }
    else {
        NSFont *labelFont = [NSFont labelFontOfSize:GRAPH_LABEL_FONT_SIZE];
        return [NSDictionary dictionaryWithObjectsAndKeys:
            labelFont, NSFontAttributeName,
            axisColor, NSForegroundColorAttributeName,
            pstyle, NSParagraphStyleAttributeName,
            nil];
    }
}

- (MGPen *)penForID:(NSInteger)aPenID
{
    if (aPenID == MGPenIDAxis) {
        return [MGPen penWithColor:axisColor width:GRAPH_LINE_WIDTH];
    }
    else if (aPenID == MGPenIDAxisOverlay) {
        return [MGPen penWithColor:axisColor width:GRAPH_AXIS_OVERLAY_WIDTH];
    }
    else {
        return [super penForID:aPenID];
    }
}

- (void)drawRect:(NSRect)rect 
{
    [super drawRect:rect];
    [self.model draw];
}
@end
