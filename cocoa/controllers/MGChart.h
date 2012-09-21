/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "HSGUIController.h"
#import "MGChartView.h"
#import "MGPen.h"
#import "MGBrush.h"
#import "PyChart.h"

@interface MGChart : HSGUIController
{
    NSMutableDictionary *fontAttrsCache;
    NSMutableDictionary *penCache;
    NSMutableDictionary *brushCache;
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (MGChartView *)view;
- (PyChart *)model;

- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID;
- (MGPen *)penForID:(NSInteger)aPenID;
- (MGBrush *)brushForID:(NSInteger)aBrushID;

/* Python callbacks */
- (void)refresh;
- (void)drawLineFrom:(NSPoint)aP1 to:(NSPoint)aP2 penID:(NSInteger)aPenID;
- (void)drawRect:(NSRect)aRect penID:(NSInteger)aPenID brushID:(NSInteger)aBrushID;
- (void)drawPieWithCenter:(NSPoint)aCenter radius:(CGFloat)aRadius startAngle:(CGFloat)aStartAngle spanAngle:(CGFloat)aSpanAngle brushID:(NSInteger)aBrushID;
- (void)drawPolygonWithPoints:(NSArray *)aPoints penID:(NSInteger)aPenID brushID:(NSInteger)aBrushID;
- (void)drawText:(NSString *)aText inRect:(NSRect)aRect withFontID:(NSInteger)aFontID;
- (NSSize)sizeForText:(NSString *)aText withFontID:(NSInteger)aFontID;
@end
