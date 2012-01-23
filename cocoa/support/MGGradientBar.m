/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGradientBar.h"

@implementation MGGradientBar
- (void)drawRect:(NSRect)rect
{
    // Define rectangles
    NSRect bounds = [self bounds];
    NSRect gradientRect = NSMakeRect(NSMinX(bounds), NSMinY(bounds), NSWidth(bounds), NSHeight(bounds) - 1);
    NSRect bottomRect = NSMakeRect(NSMinX(gradientRect), NSMinY(gradientRect), NSWidth(gradientRect), NSHeight(gradientRect) / 2);
    NSRect topRect = NSMakeRect(NSMinX(gradientRect), NSMidY(gradientRect), NSWidth(gradientRect), NSHeight(gradientRect) / 2);
    NSRect borderRect = NSMakeRect(NSMinX(bounds), NSMaxY(bounds) - 1, NSWidth(bounds), 1);
    
    // Define colors
    NSColor *bottomColor = [NSColor colorWithDeviceWhite:0.9 alpha:1.0];
    NSColor *midColor = [NSColor colorWithDeviceWhite:0.95 alpha:1.0];
    NSColor *topColor = [NSColor whiteColor];
    NSColor *borderColor = [NSColor colorWithDeviceWhite:0.62 alpha:1.0];
    
    // Draw!
    [bottomColor setFill];
    [NSBezierPath fillRect:bottomRect];
    NSGradient *gradient = [[[NSGradient alloc] initWithStartingColor:topColor endingColor:midColor] autorelease];
    [gradient drawInRect:topRect angle:90];
    [borderColor setFill];
    [NSBezierPath fillRect:borderRect];
}
@end
