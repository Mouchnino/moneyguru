#import "MGPieChartView.h"
#import "Utils.h"
#import "MGGradient.h"
#import "MGConst.h"
#import <math.h>

#define LEGEND_SQUARE_PADDING 4.0
#define TITLE_FONT_SIZE 15.0
#define LINE_WIDTH 1.0

// The fraction consts are expressed in a fraction of the total view's height
#define CHART_PADDING_FRACTION 1 / 60

#define RADIANS( degrees ) ( degrees * M_PI / 180 )

float distance(NSPoint p1, NSPoint p2)
{
    float dX = p1.x - p2.x;
    float dY = p1.y - p2.y;
    return sqrt(dX * dX + dY * dY);
}

NSPoint pointInCircle(NSPoint center, float radius, float angle)
{
    // a/sin(A) = b/sin(B) = c/sin(C) = 2R
    // the start point it (center.x + radius, center.y) and goes counterclockwise
    angle = fmod(angle, 360);
    float C = RADIANS(90);
    float A = RADIANS(fmod(angle, 90));
    float B = C - A;
    float c = radius;
    float ratio = c / sin(C);
    float b = ratio * sin(B);
    float a = ratio * sin(A);
    if (angle > 270)
        return NSMakePoint(center.x + a, center.y - b);
    else if (angle > 180)
        return NSMakePoint(center.x - b, center.y - a);
    else if (angle > 90)
        return NSMakePoint(center.x - a, center.y + b);
    else
        return NSMakePoint(center.x + b, center.y + a);
}

// Ensures that r1 is within r2. Returns a modified r1;
NSRect ensureWithin(NSRect r1, NSRect r2)
{
    float X = r1.origin.x;
    float Y = r1.origin.y;
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
    float Y = r1.origin.y;
    NSRect intersect = NSIntersectionRect(r1, r2);
    if (intersect.size.width)
    {
        Y = NSMaxY(r2) + 1; // raise it
        return NSMakeRect(NSMinX(r1), Y, NSWidth(r1), NSHeight(r1));
    }
    else
        return r1;
}

NSRect padRect(NSRect r, float padding)
{
    return NSMakeRect(NSMinX(r)-padding, NSMinY(r)-padding, NSWidth(r)+padding*2, NSHeight(r)+padding*2);
}

NSPoint rectCenter(NSRect r)
{
    return NSMakePoint(r.origin.x + NSWidth(r) / 2, r.origin.y + NSHeight(r) / 2);
}

int sortLegends(NSMutableArray *legend1, NSMutableArray *legend2, void *context)
{
    NSRect r1 = [(NSValue *)[legend1 objectAtIndex:1] rectValue];
    NSRect r2 = [(NSValue *)[legend2 objectAtIndex:1] rectValue];
    return r1.origin.y - r2.origin.y;
}

@implementation MGPieChartView
- (id)init
{
    self = [super init];
    NSMutableArray *colors = [NSMutableArray array];
    [colors addObject:[NSColor colorWithDeviceRed:0.365 green:0.737 blue:0.337 alpha:1.0]];
    [colors addObject:[NSColor colorWithDeviceRed:0.235 green:0.357 blue:0.808 alpha:1.0]];
    [colors addObject:[NSColor colorWithDeviceRed:0.714 green:0.094 blue:0.122 alpha:1.0]];
    [colors addObject:[NSColor colorWithDeviceRed:0.914 green:0.592 blue:0.035 alpha:1.0]];
    [colors addObject:[NSColor colorWithDeviceRed:0.584 green:0.129 blue:0.914 alpha:1.0]];
    [colors addObject:[NSColor darkGrayColor]];
    gradients = [[NSMutableArray array] retain];
    NSEnumerator *e = [colors objectEnumerator];
    NSColor *c;
    while (c = [e nextObject])
    {
        NSColor *light = [c blendedColorWithFraction:0.5 ofColor:[NSColor whiteColor]];
        MGGradient *g = [[MGGradient alloc] initWithStartingColor:c endingColor:light];
        [gradients addObject:[g autorelease]];
    }
    return self;
}

- (void)dealloc
{
    [gradients release];
    [super dealloc];
}

/* Override */
// In Tiger, just calling setFrame: doesn't refresh the view correctly, causing drawing glitches
// when toggling graph visibility.
- (void)setFrame:(NSRect)newFrame
{
    [super setFrame:newFrame];
    [self setNeedsDisplay:YES];
}

/* Private */
- (void)fixLegends:(NSMutableArray *)legends withCenter:(NSPoint)center
{
    // Fix legendRects overlaps. To get minimal ajustment, we must make sure that the rect that is
    // the closest to the center is moved.
    [legends sortUsingFunction:&sortLegends context:&center]; // from the highest to the lowest (on the Y axis)
    // So now, what we do to be sure we don't have overlap is that we do a double loop for the inner
    // loop, items before the current item have priority, the opposite for items after.
    for (int i=0; i<[legends count]; i++)
    {
        NSMutableArray *legend = [legends objectAtIndex:i];
        NSRect initialRect = [(NSValue *)[legend objectAtIndex:1] rectValue];
        NSRect rect = initialRect;
        for (int j=0; j<i; j++) // we move rect here
        {
            NSMutableArray *otherLegend = [legends objectAtIndex:j];
            NSRect otherRect = [(NSValue *)[otherLegend objectAtIndex:1] rectValue];
            rect = ensureOutside(rect, otherRect);
        }
        if (!NSEqualRects(rect, initialRect))
            [legend replaceObjectAtIndex:1 withObject:[NSValue valueWithRect:rect]];
        for (int j=i+1; j<[legends count]; j++) // we move otherRect here
        {
            NSMutableArray *otherLegend = [legends objectAtIndex:j];
            NSRect otherRect = [(NSValue *)[otherLegend objectAtIndex:1] rectValue];
            NSRect newOtherRect = ensureOutside(otherRect, rect);
            if (!NSEqualRects(newOtherRect, otherRect))
                [otherLegend replaceObjectAtIndex:1 withObject:[NSValue valueWithRect:newOtherRect]];
        }
    }
}

/* Drawing */
- (void)drawRect:(NSRect)rect 
{	
    [super drawRect:rect];
	// Calculate the graph dimensions
	NSSize viewSize = [self bounds].size;
    float chartPadding = viewSize.height * CHART_PADDING_FRACTION;
    float chartX = chartPadding;
    float chartY = chartPadding;
    float chartWidth = viewSize.width - chartPadding * 2;
    float chartHeight = viewSize.height - chartPadding * 2;
    
    NSFont *titleFont = [NSFont boldSystemFontOfSize:TITLE_FONT_SIZE];
    NSDictionary *titleAttributes = [NSDictionary dictionaryWithObjectsAndKeys:titleFont, NSFontAttributeName, titleColor, NSForegroundColorAttributeName, nil];
    NSSize titleSize = [title sizeWithAttributes:titleAttributes];
    float titleX = chartX + (chartWidth - titleSize.width) / 2;
    float titleY = chartY + chartHeight - titleSize.height;
    
    NSColor *legendColor = [NSColor blackColor];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSFont *legendFont = [NSFont systemFontOfSize:[ud integerForKey:TableFontSize]];
    NSDictionary *legendAttributes = [NSDictionary dictionaryWithObjectsAndKeys:legendFont, NSFontAttributeName, legendColor, NSForegroundColorAttributeName, nil];
    
	// Draw the title
    [title drawAtPoint:NSMakePoint(titleX, titleY) withAttributes:titleAttributes];
    
    float maxWidth = viewSize.width - (chartPadding * 2);
    float maxHeight = titleY - chartPadding;
    float circleSize = maxWidth > maxHeight ? maxHeight : maxWidth;
    float radius = circleSize / 2;
    NSPoint center = NSMakePoint(viewSize.width / 2, titleY - chartPadding - radius);
    float circleX = center.x - radius;
    float circleY = center.y - radius;
    NSColor *lineColor = [NSColor blackColor];
    [lineColor setStroke];
    NSRect circleRect = NSMakeRect(circleX, circleY, circleSize, circleSize);
    
    // Draw the pie
    NSEnumerator *e = [data objectEnumerator];
    NSArray *pair;
    float total = 0;
    while (pair = [e nextObject])
        total += n2f([pair objectAtIndex:1]);
    NSMutableArray *legends = [NSMutableArray array];
    float startAngle = 0;
    for (int i=0; i<[data count]; i++)
    {
        pair = [data objectAtIndex:i];
        MGGradient *gradient = [gradients objectAtIndex:i % [gradients count]];
        float fraction = n2f([pair objectAtIndex:1]) / total;
        float angle = fraction * 360;
        float endAngle = startAngle + angle;
        
        NSBezierPath *slice = [NSBezierPath bezierPath];
        [slice moveToPoint:center];
        [slice appendBezierPathWithArcWithCenter:center radius:radius startAngle:startAngle endAngle:endAngle];
        [slice lineToPoint:center];
        [NSGraphicsContext saveGraphicsState];
        [slice addClip];
        [self fillRect:circleRect withGradient:gradient];
        [NSGraphicsContext restoreGraphicsState];
        [slice setLineWidth:LINE_WIDTH];
        [slice stroke];
        
        NSString *legendText = [pair objectAtIndex:0];
        NSPoint legendPoint = pointInCircle(center, radius, startAngle + (angle / 2));
        NSSize legendSize = [legendText sizeWithAttributes:legendAttributes];
        legendPoint.x -= legendSize.width / 2;
        if (legendPoint.y > center.y)
            legendPoint.y -= legendSize.height;
        NSRect legendRect = NSMakeRect(legendPoint.x, legendPoint.y, legendSize.width, legendSize.height);
        legendRect = padRect(legendRect, LEGEND_SQUARE_PADDING);
        legendRect = ensureWithin(legendRect, [self bounds]);
        NSMutableArray *legend = [NSMutableArray arrayWithObjects:legendText,[NSValue valueWithRect:legendRect],gradient,nil];
        [legends addObject:legend];
        
        startAngle = endAngle;
    }
    
    [self fixLegends:legends withCenter:center];
    
    // Draw the legend rects
    for (int i=0; i<[legends count]; i++)
    {
        NSMutableArray *legend = [legends objectAtIndex:i];
        NSString *legendText = [legend objectAtIndex:0];
        NSRect legendRect = [[legend objectAtIndex:1] rectValue];
        MGGradient *gradient = [legend objectAtIndex:2];
        
        NSBezierPath *path = [NSBezierPath bezierPathWithRect:legendRect];
        [path setLineWidth:LINE_WIDTH];
        [backgroundColor setFill];
        [[gradient startingColor] setStroke];
        [path fill];
        [path stroke];
        NSPoint legendPoint = NSMakePoint(NSMinX(legendRect) + LEGEND_SQUARE_PADDING, NSMinY(legendRect) + LEGEND_SQUARE_PADDING);
        [legendText drawAtPoint:legendPoint withAttributes:legendAttributes];
    }
}
@end
