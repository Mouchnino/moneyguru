/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChart.h"
#import "HSPyUtil.h"
#import "Utils.h"

static NSGradient* gradientFromColor(NSColor *aColor)
{
    NSColor *light = [aColor blendedColorWithFraction:0.5 ofColor:[NSColor whiteColor]];
    return [[[NSGradient alloc] initWithStartingColor:aColor endingColor:light] autorelease];
}

@implementation MGChart
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyChart *m = [[PyChart alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"ChartView", self)];
    [m release];
    fontAttrsCache = [[NSMutableDictionary dictionary] retain];
    gradientsCache = [[NSMutableDictionary dictionary] retain];
    return self;
}

- (void)dealloc
{
    [fontAttrsCache release];
    [gradientsCache release];
    [super dealloc];
}

/* Override */
- (MGChartView *)view
{
    return (MGChartView *)view;
}

- (void)setView:(MGChartView *)aView
{
    [super setView:aView];
    if (aView != nil) {
        [aView setModel:[self model]];
    }
}

- (PyChart *)model
{
    return (PyChart *)model;
}

- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID
{
    NSDictionary *result = [fontAttrsCache objectForKey:i2n(aFontID)];
    if (result == nil) {
        result = [self.view fontAttributesForID:aFontID];
        [fontAttrsCache setObject:result forKey:i2n(aFontID)];
    }
    return result;
}

- (NSGradient *)gradientForIndex:(NSInteger)aColorIndex
{
    NSGradient *result = [gradientsCache objectForKey:i2n(aColorIndex)];
    if (result == nil) {
        NSColor *color = [self.view colorForIndex:aColorIndex];
        result = gradientFromColor(color);
        [gradientsCache setObject:result forKey:i2n(aColorIndex)];
    }
    return result;
}

/* Python callbacks */
- (void)refresh
{
    [[self view] setData:[[self model] data]];
    [[self view] setTitle:[[self model] title]];
    [[self view] setCurrency:[[self model] currency]];
    [[self view] setNeedsDisplay:YES];
}

- (void)drawLineFrom:(NSPoint)aP1 to:(NSPoint)aP2 colorIndex:(NSInteger)aColorIndex
{
    NSColor *color = [self.view colorForIndex:aColorIndex];
    [self.view drawLineFrom:aP1 to:aP2 colorIndex:color];
}

- (void)drawRect:(NSRect)aRect lineColor:(NSInteger)aLineColor bgColor:(NSInteger)aBgColor
{
    NSColor *lineColor = [self.view colorForIndex:aLineColor];
    NSColor *bgColor = [self.view colorForIndex:aBgColor];
    [self.view drawRect:aRect lineColor:lineColor bgColor:bgColor];
}

- (void)drawPieWithCenter:(NSPoint)aCenter radius:(CGFloat)aRadius startAngle:(CGFloat)aStartAngle spanAngle:(CGFloat)aSpanAngle colorIndex:(NSInteger)aColorIndex
{
    NSGradient *gradient = [self gradientForIndex:aColorIndex];
    [self.view drawPieWithCenter:aCenter radius:aRadius startAngle:aStartAngle spanAngle:aSpanAngle gradient:gradient];
}

- (void)drawText:(NSString *)aText inRect:(NSRect)aRect withFontID:(NSInteger)aFontID
{
    NSDictionary *attrs = [self fontAttributesForID:aFontID];
    [self.view drawText:aText inRect:aRect withAttributes:attrs];
}

- (NSSize)sizeForText:(NSString *)aText withFontID:(NSInteger)aFontID
{
    NSDictionary *attrs = [self fontAttributesForID:aFontID];
    return [aText sizeWithAttributes:attrs];
}
@end
