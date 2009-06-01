#import <Cocoa/Cocoa.h>

@interface MGDoubleView : NSView
{
    NSView *firstView;
    NSView *secondView;
}
- (NSView *)firstView;
- (void)setFirstView:(NSView *)view;
- (NSView *)secondView;
- (void)setSecondView:(NSView *)view;
@end