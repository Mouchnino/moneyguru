/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChartView.h"
#import "Utils.h"

@implementation MGChartView
- (void)commonInit
{
    backgroundColor = [[NSColor whiteColor] retain];
    titleColor = [[NSColor grayColor] retain];
}

- (id)init
{
    self = [super init];
    [self commonInit];
    return self;
}

- (id)initWithFrame:(NSRect)frameRect
{
    self = [super initWithFrame:frameRect];
    [self commonInit];
    return self;
}

- (void)dealloc
{
    [backgroundColor release];
    [titleColor release];
    [model release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGChartView *result = [[[self class] alloc] init];
    [result setModel:model];
    return result;
}

- (void)drawRect:(NSRect)rect
{
    [backgroundColor setFill];
	[NSBezierPath fillRect:rect];
    [self.model draw];
}

- (BOOL)isOpaque
{
	return YES;
}

- (void)setFrameSize:(NSSize)newSize
{
    [super setFrameSize:newSize];
    [[self model] setViewWidth:newSize.width height:newSize.height];
}

- (PyChart *)model
{
    return model;
}

- (void)setModel:(PyChart *)aModel
{
    [model release];
    model = [aModel retain];
}

- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID
{
    /* Returns a dictionary with the appropriate elements for a usage in NSString.drawText or
       NSString.sizeWithAttributes().
    */
    return nil;
}

- (MGPen *)penForID:(NSInteger)aPenID
{
    return nil;
}

- (MGBrush *)brushForID:(NSInteger)aBrushID
{
    return nil;
}

- (void)drawLineFrom:(NSPoint)aP1 to:(NSPoint)aP2 pen:(MGPen *)aPen
{
    NSBezierPath *path = [NSBezierPath bezierPath];
    [path moveToPoint:aP1];
    [path lineToPoint:aP2];
    [aPen stroke:path];
}

- (void)drawRect:(NSRect)aRect pen:(MGPen *)aPen brush:(MGBrush *)aBrush
{
    NSBezierPath *path = [NSBezierPath bezierPathWithRect:aRect];
    [aBrush fill:path];
    [aPen stroke:path];
}

- (void)drawPieWithCenter:(NSPoint)aCenter radius:(CGFloat)aRadius startAngle:(CGFloat)aStartAngle spanAngle:(CGFloat)aSpanAngle brush:(MGBrush *)aBrush
{
    CGFloat endAngle = aStartAngle + aSpanAngle;
    CGFloat circleX = aCenter.x - aRadius;
    CGFloat circleY = aCenter.y - aRadius;
    CGFloat diameter = aRadius * 2;
    NSRect circleRect = NSMakeRect(circleX, circleY, diameter, diameter);
    
    NSBezierPath *slice = [NSBezierPath bezierPath];
    [slice moveToPoint:aCenter];
    [slice appendBezierPathWithArcWithCenter:aCenter radius:aRadius startAngle:aStartAngle endAngle:endAngle];
    [slice lineToPoint:aCenter];
    [NSGraphicsContext saveGraphicsState];
    [slice addClip];
    [aBrush.gradient drawInRect:circleRect angle:90];
    [NSGraphicsContext restoreGraphicsState];
    [[NSColor blackColor] setStroke];
    [slice setLineWidth:1.0];
    [slice stroke];
}

- (void)drawPolygonWithPoints:(NSArray *)aPoints pen:(MGPen *)aPen brush:(MGBrush *)aBrush
{
    NSInteger pointCount = [aPoints count];
    if (pointCount < 2) {
        return;
    }
    NSBezierPath *path = [NSBezierPath bezierPath];
    NSArray *pointList = [aPoints objectAtIndex:0];
    NSPoint pt = NSMakePoint(n2f([pointList objectAtIndex:0]), n2f([pointList objectAtIndex:1]));
    [path moveToPoint:pt];
    NSArray *restOfPoints = [aPoints subarrayWithRange:NSMakeRange(1, pointCount-1)];
    for (pointList in restOfPoints) {
        pt = NSMakePoint(n2f([pointList objectAtIndex:0]), n2f([pointList objectAtIndex:1]));
        [path lineToPoint:pt];
    }
    [aBrush fill:path];
    [aPen stroke:path];
}

- (void)drawText:(NSString *)aText inRect:(NSRect)aRect withAttributes:(NSDictionary *)aAttrs
{
    [NSGraphicsContext saveGraphicsState];
    [aText drawInRect:aRect withAttributes:aAttrs];
    [NSGraphicsContext restoreGraphicsState];
}
@end