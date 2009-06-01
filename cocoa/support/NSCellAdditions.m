#import "NSCellAdditions.h"

@implementation NSCell(NSCellAdditions)
- (void)drawTransparentBezelWithFrame:(NSRect)frame inView:(NSView *)controlView withLeftSide:(BOOL)withLeftSide {
    // Figure out the geometry. Note: NSButton uses flipped coordinates
    NSRect leftSide = NSMakeRect(NSMinX(frame), NSMinY(frame), 1, NSHeight(frame));
    NSRect rightSide = NSMakeRect(NSMaxX(frame) - 1, NSMinY(frame), 1, NSHeight(frame));
    
    // Define colors
    NSColor *borderColor = [NSColor colorWithDeviceWhite:0.62 alpha:1.0];
    NSColor *highlightColor = [NSColor colorWithDeviceWhite:0.0 alpha:0.35];
    
    // Draw the sides of the button
    [borderColor setFill];
    if (withLeftSide)
        [NSBezierPath fillRect:leftSide];
    [NSBezierPath fillRect:rightSide];
    
    // Draw the highlight
    if ([self isHighlighted])
    {
        [highlightColor setFill];
        [NSBezierPath fillRect:frame];
    }
}
@end