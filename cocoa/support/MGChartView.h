/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyChart.h"

@interface MGChartView : NSView <NSCopying>
{
    PyChart *model;
    NSArray *data;
    NSString *title;
    NSString *currency;
    NSColor *backgroundColor;
    NSColor *titleColor;
}
- (PyChart *)model;
- (void)setModel:(PyChart *)aModel;
- (void)setData:(NSArray *)aData;
- (void)setTitle:(NSString *)aTitle;
- (void)setCurrency:(NSString *)aCurrency;
- (NSDictionary *)fontAttributesForID:(NSInteger)aFontID;
- (NSColor *)colorForIndex:(NSInteger)aColorIndex;
- (NSGradient *)gradientFromColor:(NSColor *)aColor;
- (void)drawLineFrom:(NSPoint)aP1 to:(NSPoint)aP2 colorIndex:(NSInteger)aColorIndex;
- (void)drawRect:(NSRect)aRect lineColor:(NSInteger)aLineColor bgColor:(NSInteger)aBgColor;
- (void)drawPieWithCenter:(NSPoint)aCenter radius:(CGFloat)aRadius startAngle:(CGFloat)aStartAngle spanAngle:(CGFloat)aSpanAngle colorIndex:(NSInteger)aColorIndex;
- (void)drawText:(NSString *)aText inRect:(NSRect)aRect withAttributes:(NSDictionary *)aAttrs;
@end