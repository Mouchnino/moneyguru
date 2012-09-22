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

static NSArray* arrayWithoutLastElement(NSArray *a) {
    if ([a count]) {
        return [a subarrayWithRange:NSMakeRange(0, [a count]-1)];
    }
    else {
        return a;
    }
}

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
    [xLabels release];
    [yLabels release];
    [xTickMarks release];
    [yTickMarks release];
    [fillGradient release];
    [futureGradient release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGGraphView *result = [super copyWithZone:zone];
    [result setMinX:minX];
    [result setMaxX:maxX];
    [result setMinY:minY];
    [result setMaxY:maxY];
    [result setXToday:xToday];
    [result setXLabels:xLabels];
    [result setYLabels:yLabels];
    [result setXTickMarks:xTickMarks];
    [result setYTickMarks:yTickMarks];
    return result;
}

- (PyGraph *)model
{
    return (PyGraph *)[super model];
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

- (void)setMinX:(CGFloat)aMinX
{
    minX = aMinX;
}

- (void)setMaxX:(CGFloat)aMaxX
{
    maxX = aMaxX;
}

- (void)setMinY:(CGFloat)aMinY
{
    minY = aMinY;
}

- (void)setMaxY:(CGFloat)aMaxY
{
    maxY = aMaxY;
}

- (void)setXToday:(CGFloat)aXToday
{
    xToday = aXToday;
}

- (void)setXLabels:(NSArray *)aXLabels
{
    [xLabels autorelease];
    xLabels = [aXLabels retain];
}

- (void)setYLabels:(NSArray *)aYLabels
{
    [yLabels autorelease];
    yLabels = [aYLabels retain];
}

- (void)setXTickMarks:(NSArray *)aXTickMarks
{
    [xTickMarks autorelease];
    xTickMarks = [aXTickMarks retain];
}

- (void)setYTickMarks:(NSArray *)aYTickMarks
{
    [yTickMarks autorelease];
    yTickMarks = [aYTickMarks retain];
}
@end
