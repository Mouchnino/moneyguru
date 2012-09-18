/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGPieChartView.h"
#import "Utils.h"
#import "MGConst.h"
#import "HSGeometry.h"
#import <math.h>

#define LEGEND_PADDING 4.0
#define TITLE_FONT_SIZE 15.0
#define LINE_WIDTH 1.0
#define CHART_PADDING 6.0

// Ensures that r1 is within r2. Returns a modified r1;
NSRect ensureWithin(NSRect r1, NSRect r2)
{
    CGFloat X = r1.origin.x;
    CGFloat Y = r1.origin.y;
    if (NSMaxX(r1) > NSMaxX(r2))
        X = NSMaxX(r2) - NSWidth(r1);
    if (NSMaxY(r1) > NSMaxY(r2))
        Y = NSMaxY(r2) - NSHeight(r1);
    if (NSMinX(r1) < NSMinX(r2))
        X = r2.origin.x;
    if (NSMinY(r1) < NSMinY(r2))
        Y = r2.origin.y;
    return NSMakeRect(X, Y, r1.size.width, r1.size.height);
}

// Ensures that r1 does not intersect with r2. Returns a modified r1;
NSRect ensureOutside(NSRect r1, NSRect r2)
{
    CGFloat Y = r1.origin.y;
    NSRect intersect = NSIntersectionRect(r1, r2);
    if (intersect.size.width)
    {
        Y = NSMaxY(r2) + 1; // raise it
        return NSMakeRect(NSMinX(r1), Y, NSWidth(r1), NSHeight(r1));
    }
    else
        return r1;
}

NSRect padRect(NSRect r, CGFloat padding)
{
    return NSMakeRect(NSMinX(r)-padding, NSMinY(r)-padding, NSWidth(r)+padding*2, NSHeight(r)+padding*2);
}

NSPoint rectCenter(NSRect r)
{
    return NSMakePoint(r.origin.x + NSWidth(r) / 2, r.origin.y + NSHeight(r) / 2);
}

@implementation MGPieChartView
- (id)init
{
    self = [super init];
    gradients = nil;
    return self;
}

- (void)dealloc
{
    [gradients release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGPieChartView *result = [super copyWithZone:zone];
    [result setGradients:gradients];
    return result;
}

- (void)setGradients:(NSArray *)aGradients
{
    [gradients release];
    gradients = [aGradients retain];
}

- (void)setColors:(NSArray *)colors
{
    NSMutableArray *grads = [NSMutableArray array];
    for (NSColor *c in colors) {
        NSColor *light = [c blendedColorWithFraction:0.5 ofColor:[NSColor whiteColor]];
        NSGradient *g = [[NSGradient alloc] initWithStartingColor:c endingColor:light];
        [grads addObject:g];
        [g release];
    }
    [self setGradients:grads];
}

- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID
{
    NSFont *titleFont = [NSFont boldSystemFontOfSize:15.0];
    NSMutableParagraphStyle *pstyle = [[[NSMutableParagraphStyle alloc] init] autorelease];
    [pstyle setAlignment:NSCenterTextAlignment];
    return [NSDictionary dictionaryWithObjectsAndKeys:
        titleFont, NSFontAttributeName,
        [NSColor grayColor], NSForegroundColorAttributeName,
        pstyle, NSParagraphStyleAttributeName,
        nil];
}

- (NSGradient *)gradientForIndex:(NSInteger)aColorIndex
{
    return [gradients objectAtIndex:aColorIndex];
}

/* Drawing */
- (void)drawRect:(NSRect)rect 
{	
    [super drawRect:rect];
	// Calculate the graph dimensions
    NSSize viewSize = [self bounds].size;
    CGFloat chartX = CHART_PADDING;
    CGFloat chartY = CHART_PADDING;
    CGFloat chartWidth = viewSize.width - CHART_PADDING * 2;
    CGFloat chartHeight = viewSize.height - CHART_PADDING * 2;
    
    NSFont *titleFont = [NSFont boldSystemFontOfSize:TITLE_FONT_SIZE];
    NSDictionary *titleAttributes = [NSDictionary dictionaryWithObjectsAndKeys:titleFont, NSFontAttributeName, titleColor, NSForegroundColorAttributeName, nil];
    NSSize titleSize = [title sizeWithAttributes:titleAttributes];
    CGFloat titleX = chartX + (chartWidth - titleSize.width) / 2;
    CGFloat titleY = chartY + chartHeight - titleSize.height;
    
    NSColor *legendColor = [NSColor blackColor];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSFont *legendFont = [NSFont systemFontOfSize:[ud integerForKey:TableFontSize]];
    NSDictionary *legendAttributes = [NSDictionary dictionaryWithObjectsAndKeys:legendFont, NSFontAttributeName, legendColor, NSForegroundColorAttributeName, nil];
    
    [self.model draw];
	// Draw the title
    // [title drawAtPoint:NSMakePoint(titleX, titleY) withAttributes:titleAttributes];
    
    CGFloat maxWidth = viewSize.width - (CHART_PADDING * 2);
    CGFloat maxHeight = titleY - CHART_PADDING;
    CGFloat circleSize = maxWidth > maxHeight ? maxHeight : maxWidth;
    CGFloat radius = circleSize / 2;
    NSPoint center = NSMakePoint(viewSize.width / 2, titleY - CHART_PADDING - radius);
    CGFloat circleX = center.x - radius;
    CGFloat circleY = center.y - radius;
    NSColor *lineColor = [NSColor blackColor];
    [lineColor setStroke];
    NSRect circleRect = NSMakeRect(circleX, circleY, circleSize, circleSize);
    
    // Draw the pie
    CGFloat total = 0;
    for (NSArray *dataPoint in data) {
        total += n2f([dataPoint objectAtIndex:1]);
    }
    NSMutableArray *legends = [NSMutableArray array];
    CGFloat startAngle = 0;
    for (NSArray *dataPoint in data) {
        NSInteger colorIndex = n2i([dataPoint objectAtIndex:2]);
        NSGradient *gradient = [gradients objectAtIndex:colorIndex];
        CGFloat fraction = n2f([dataPoint objectAtIndex:1]) / total;
        CGFloat angle = fraction * 360;
        CGFloat endAngle = startAngle + angle;
        
        // NSBezierPath *slice = [NSBezierPath bezierPath];
        // [slice moveToPoint:center];
        // [slice appendBezierPathWithArcWithCenter:center radius:radius startAngle:startAngle endAngle:endAngle];
        // [slice lineToPoint:center];
        // [NSGraphicsContext saveGraphicsState];
        // [slice addClip];
        // [gradient drawInRect:circleRect angle:90];
        // [NSGraphicsContext restoreGraphicsState];
        // [slice setLineWidth:LINE_WIDTH];
        // [slice stroke];
        
        NSString *legendText = [dataPoint objectAtIndex:0];
        NSPoint baseLegendPoint = pointInCircle(center, radius, deg2rad(startAngle + (angle / 2)));
        NSSize legendSize = [legendText sizeWithAttributes:legendAttributes];
        NSPoint legendPoint = NSMakePoint(baseLegendPoint.x - (legendSize.width / 2), baseLegendPoint.y);
        NSRect legendRect = NSMakeRect(legendPoint.x, legendPoint.y, legendSize.width, legendSize.height);
        legendRect = padRect(legendRect, LEGEND_PADDING);
        legendRect = ensureWithin(legendRect, [self bounds]);
        NSMutableArray *legend = [NSMutableArray arrayWithObjects:legendText,
            [NSValue valueWithPoint:baseLegendPoint], [NSValue valueWithRect:legendRect],gradient,nil];
        [legends addObject:legend];
        
        startAngle = endAngle;
    }
    
    // Fix legend rects
    NSRect previousRect = NSMakeRect(0, 0, 0, 0);
    for (NSMutableArray *legend in legends)
    {
        NSRect r = [(NSValue *)[legend objectAtIndex:2] rectValue];
        if (rectCenter(r).x < center.x) // send left
            r = NSMakeRect(chartX, NSMinY(r), NSWidth(r), NSHeight(r));
        else // send right
            r = NSMakeRect(chartX + chartWidth - NSWidth(r), NSMinY(r), NSWidth(r), NSHeight(r));
        r = ensureOutside(r, previousRect);
        previousRect = r;
        [legend replaceObjectAtIndex:2 withObject:[NSValue valueWithRect:r]];
    }
    
    // Draw the legend rects
    for (NSArray *legend in legends)
    {
        NSString *legendText = [legend objectAtIndex:0];
        NSPoint baseLegendPoint = [[legend objectAtIndex:1] pointValue];
        NSRect legendRect = [[legend objectAtIndex:2] rectValue];
        NSGradient *gradient = [legend objectAtIndex:3];
        
        NSBezierPath *path = [NSBezierPath bezierPathWithRect:legendRect];
        [path setLineWidth:LINE_WIDTH];
        [backgroundColor setFill];
        NSColor *startingColor = [gradient interpolatedColorAtLocation:0.0];
        [startingColor setStroke];
        [path fill];
        [path stroke];
        NSPoint legendPoint = NSMakePoint(NSMinX(legendRect) + LEGEND_PADDING, NSMinY(legendRect) + LEGEND_PADDING);
        [legendText drawAtPoint:legendPoint withAttributes:legendAttributes];
        
        // We don't use NSPointInRect and only verify if baseLegendPoint is within the *X* bounds
        // of the rect. This is because a legend rect might have been displaced vertically because
        // of its proximity with another legend. When that happens, a line is drawn and this line
        // is ugly.
        if ((baseLegendPoint.x < NSMinX(legendRect)) || (baseLegendPoint.x > NSMaxX(legendRect))) {
            path = [NSBezierPath bezierPath];
            if (baseLegendPoint.x < center.x)
                [path moveToPoint:NSMakePoint(NSMaxX(legendRect), NSMidY(legendRect))];
            else
                [path moveToPoint:NSMakePoint(NSMinX(legendRect), NSMidY(legendRect))];
            [path lineToPoint:baseLegendPoint];
            [path setLineWidth:LINE_WIDTH];
            [startingColor setStroke];
            [path stroke];
        }
    }
}
@end
