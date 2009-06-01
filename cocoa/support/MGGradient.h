#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>

@interface MGGradient : NSObject {
    NSColor *startingColor;
    NSColor *endingColor;
}
- (MGGradient *)initWithStartingColor:(NSColor *)startingColor endingColor:(NSColor *)endingColor;
- (void)drawVerticallyInRect:(NSRect)rect;
- (NSColor *)startingColor;
- (NSColor *)endingColor;
@end
