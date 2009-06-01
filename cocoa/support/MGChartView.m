#import "MGChartView.h"

@implementation MGChartView
- (id)init
{
    self = [super init];
    backgroundColor = [[NSColor whiteColor] retain];
    titleColor = [[NSColor grayColor] retain];
    return self;
}

- (void)dealloc
{
    [backgroundColor release];
    [titleColor release];
    [data release];
    [title release];
    [currency release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGChartView *result = [[[self class] alloc] init];
    [result setData:data];
    [result setTitle:title];
    [result setCurrency:currency];
    return result;
}

- (void)drawRect:(NSRect)rect
{
    [backgroundColor setFill];
	[NSBezierPath fillRect:rect];
}

- (BOOL)isOpaque
{
	return YES;
}

- (void)fillRect:(NSRect)aRect withGradient:(MGGradient *)aGradient
{
    if ([NSGraphicsContext currentContextDrawingToScreen])
        [aGradient drawVerticallyInRect:aRect];
    else
    {   // Gradients don't work in a printing context
        [[aGradient startingColor] setFill];
        [NSBezierPath fillRect:aRect];
    }
}

- (void)setData:(NSArray *)aData
{
    [data autorelease];
    data = [aData retain];
}

- (void)setTitle:(NSString *)aTitle
{
    [title autorelease];
    title = [aTitle retain];
}

- (void)setCurrency:(NSString *)aCurrency
{
    [currency autorelease];
    currency = [aCurrency retain];
}
@end