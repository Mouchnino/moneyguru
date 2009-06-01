#import "MGDoubleView.h"

@implementation MGDoubleView
- (void)resizeSubviewsWithOldSize:(NSSize)oldBoundsSize
{
    //[super resizeSubviewsWithOldSize:oldBoundsSize];
    if ((firstView == nil) || (secondView == nil))
        return;
    NSRect b = [self bounds];
    if (NSHeight(b) >= NSWidth(b))
    {
        // Vertical
        [firstView setFrame:NSMakeRect(NSMinX(b), NSMinY(b) + NSHeight(b) / 2, NSWidth(b), NSHeight(b) / 2)];
        [secondView setFrame:NSMakeRect(NSMinX(b), NSMinY(b), NSWidth(b), NSHeight(b) / 2)];
    }
    else
    {
        // Horizontal
        [firstView setFrame:NSMakeRect(NSMinX(b), NSMinY(b), NSWidth(b) / 2, NSHeight(b))];
        [secondView setFrame:NSMakeRect(NSMinX(b) + NSWidth(b) / 2, NSMinY(b), NSWidth(b) / 2, NSHeight(b))];
    }
}

- (NSView *)firstView
{
    return firstView;
}

- (void)setFirstView:(NSView *)view
{
    if (firstView != nil)
        [firstView removeFromSuperview];
    firstView = view;
    [self addSubview:firstView];
    [self resizeSubviewsWithOldSize:[self bounds].size];
}

- (NSView *)secondView
{
    return secondView;
}

- (void)setSecondView:(NSView *)view
{
    if (secondView != nil)
        [secondView removeFromSuperview];
    secondView = view;
    [self addSubview:secondView];
    [self resizeSubviewsWithOldSize:[self bounds].size];
}
@end