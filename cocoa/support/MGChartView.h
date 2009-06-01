#import <Cocoa/Cocoa.h>
#import "MGGradient.h"

@interface MGChartView : NSView <NSCopying>
{
    NSArray *data;
    NSString *title;
    NSString *currency;
    NSColor *backgroundColor;
    NSColor *titleColor;
}
- (void)fillRect:(NSRect)aRect withGradient:(MGGradient *)aGradient;

- (void)setData:(NSArray *)aData;
- (void)setTitle:(NSString *)aTitle;
- (void)setCurrency:(NSString *)aCurrency;

@end