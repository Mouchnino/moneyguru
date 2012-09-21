/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChart.h"
#import "HSPyUtil.h"
#import "Utils.h"

@implementation MGChart
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyChart *m = [[PyChart alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"ChartView", self)];
    [m release];
    fontAttrsCache = [[NSMutableDictionary dictionary] retain];
    penCache = [[NSMutableDictionary dictionary] retain];
    brushCache = [[NSMutableDictionary dictionary] retain];
    return self;
}

- (void)dealloc
{
    [fontAttrsCache release];
    [penCache release];
    [brushCache release];
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

- (MGPen *)penForID:(NSInteger)aPenID
{
    if (aPenID < 0) {
        return [MGPen nullPen];
    }
    MGPen *result = [penCache objectForKey:i2n(aPenID)];
    if (result == nil) {
        result = [self.view penForID:(NSInteger)aPenID];
        [penCache setObject:result forKey:i2n(aPenID)];
    }
    return result;
}

- (MGBrush *)brushForID:(NSInteger)aBrushID
{
    if (aBrushID < 0) {
        return [MGBrush nullBrush];
    }
    MGBrush *result = [brushCache objectForKey:i2n(aBrushID)];
    if (result == nil) {
        result = [self.view brushForID:aBrushID];
        [brushCache setObject:result forKey:i2n(aBrushID)];
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

- (void)drawLineFrom:(NSPoint)aP1 to:(NSPoint)aP2 penID:(NSInteger)aPenID
{
    MGPen *pen = [self.view penForID:aPenID];
    [self.view drawLineFrom:aP1 to:aP2 pen:pen];
}

- (void)drawRect:(NSRect)aRect penID:(NSInteger)aPenID brushID:(NSInteger)aBrushID
{
    MGPen *pen = [self.view penForID:aPenID];
    MGBrush *brush = [self.view brushForID:aBrushID];
    [self.view drawRect:aRect pen:pen brush:brush];
}

- (void)drawPieWithCenter:(NSPoint)aCenter radius:(CGFloat)aRadius startAngle:(CGFloat)aStartAngle spanAngle:(CGFloat)aSpanAngle brushID:(NSInteger)aBrushID
{
    MGBrush *brush = [self.view brushForID:aBrushID];
    [self.view drawPieWithCenter:aCenter radius:aRadius startAngle:aStartAngle spanAngle:aSpanAngle brush:brush];
}

- (void)drawPolygonWithPoints:(NSArray *)aPoints penID:(NSInteger)aPenID brushID:(NSInteger)aBrushID
{
    MGPen *pen = [self.view penForID:aPenID];
    MGBrush *brush = [self.view brushForID:aBrushID];
    [self.view drawPolygonWithPoints:aPoints pen:pen brush:brush];
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
