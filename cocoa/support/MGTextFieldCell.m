/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTextFieldCell.h"
#import "MGOutlineView.h"

#define ARROW_WIDTH 12.0
#define ARROW_HEIGHT 12.0
#define ARROW_PADDING 4.0
#define BUTTON_WIDTH 12.0
#define BUTTON_HEIGHT 12.0
#define BUTTON_PADDING 4.0

@implementation MGTextFieldCell
/* Private */
- (NSRect)textRectForBounds:(NSRect)bounds
{
    if (indent)
    {
        bounds = NSMakeRect(NSMinX(bounds) + indent, NSMinY(bounds), NSWidth(bounds) - indent, NSHeight(bounds));
    }
    if (hasArrow)
    {
        bounds = NSMakeRect(NSMinX(bounds), NSMinY(bounds), NSWidth(bounds) - ARROW_WIDTH - ARROW_PADDING * 2, NSHeight(bounds));
    }
    return bounds;
}

- (NSRect)arrowRectForBounds:(NSRect)bounds
{
    if (hasArrow)
    {
        float y_offset = (NSHeight(bounds) - 1.0 - ARROW_HEIGHT) / 2.0;
        float x_offset = ARROW_WIDTH + ARROW_PADDING;
        return NSMakeRect(NSMaxX(bounds) - x_offset, NSMinY(bounds) + y_offset, ARROW_WIDTH, ARROW_HEIGHT);
    }
    else
    {
        return NSZeroRect;
    }
}

- (NSRect)buttonRectForBounds:(NSRect)bounds
{
    if (buttonImageName == nil)
        return NSZeroRect;
    float maxX = NSMaxX(bounds);
    if (hasArrow)
        maxX = NSMinX([self arrowRectForBounds:bounds]);
    float offsetY = (NSHeight(bounds) - 1.0 - BUTTON_HEIGHT) / 2.0;
    float offsetX = BUTTON_WIDTH + BUTTON_PADDING;
    return NSMakeRect(maxX - offsetX, NSMinY(bounds) + offsetY, BUTTON_WIDTH, BUTTON_HEIGHT);
}

/* Public */
- (void)setIndent:(int)value
{
    indent = value;
}

- (void)setHasArrow:(BOOL)value
{
    hasArrow = value;
}

- (void)setHasDarkBackground:(BOOL)value
{
    hasDarkBackground = value;
}

- (void)setArrowTarget:(id)value
{
    arrowTarget = value;
}

- (void)setArrowAction:(SEL)value
{
    arrowAction = value;
}

- (void)setButtonImageName:(NSString *)aImageName
{
    buttonImageName = aImageName;
}

- (void)setButtonTarget:(id)value
{
    buttonTarget = value;
}

- (void)setButtonAction:(SEL)value
{
    buttonAction = value;
}
        
/* NSCopying (we implement it because, apparently, NSTableView likes to copy cells) */

- (id)copyWithZone:(NSZone *)zone
{
    MGTextFieldCell *result = [super copyWithZone:zone];
    [result setIndent:indent];
    [result setHasArrow:hasArrow];
    [result setArrowTarget:arrowTarget];
    [result setArrowAction:arrowAction];
    [result setButtonImageName:buttonImageName];
    [result setButtonTarget:buttonTarget];
    [result setButtonAction:buttonAction];
    return result;
}

/* NSCell */

+ (BOOL)prefersTrackingUntilMouseUp {
    // We want to have trackMouse:inRect:ofView:untilMouseUp: always track until the mouse is up
    return YES;
}

- (void)drawInteriorWithFrame:(NSRect)cellFrame inView:(NSView *)controlView
{
    [super drawInteriorWithFrame:[self textRectForBounds:cellFrame] inView:controlView];
    
    /* Add the little arrow if requested */
    if (hasArrow)
    {
        NSRect arrowRect = [self arrowRectForBounds:cellFrame];
        NSString *imageName = hasDarkBackground ? @"right_arrow_white_12" : @"right_arrow_gray_12";
        NSImage *arrowImage = [NSImage imageNamed:imageName];
        [arrowImage drawInRect:arrowRect fromRect:NSZeroRect operation:NSCompositeSourceOver fraction:0.8];
    }
    
    // Add a little button next to the arrow if we have an image set for it
    if (buttonImageName != nil)
    {
        NSRect buttonRect = [self buttonRectForBounds:cellFrame];
        NSImage *buttonImage = [NSImage imageNamed:buttonImageName];
        [buttonImage drawInRect:buttonRect fromRect:NSZeroRect operation:NSCompositeSourceOver fraction:1];
    }    
}

- (NSUInteger)hitTestForEvent:(NSEvent *)event inRect:(NSRect)cellFrame ofView:(NSView *)controlView
{
    NSPoint point = [controlView convertPoint:[event locationInWindow] fromView:nil];
    if (hasArrow) {
        NSRect arrowRect = [self arrowRectForBounds:cellFrame];
        if (NSMouseInRect(point, arrowRect, [controlView isFlipped]))
            return NSCellHitTrackableArea;
    }
    if (buttonImageName != nil) {
        NSRect buttonRect = [self buttonRectForBounds:cellFrame];
        if (NSMouseInRect(point, buttonRect, [controlView isFlipped]))
            return NSCellHitTrackableArea;
    }
    return [super hitTestForEvent:event inRect:cellFrame ofView:controlView];
}

- (BOOL)trackMouse:(NSEvent *)event inRect:(NSRect)cellFrame ofView:(NSView *)controlView untilMouseUp:(BOOL)untilMouseUp
{
    NSPoint point = [controlView convertPoint:[event locationInWindow] fromView:nil];
    if (hasArrow)
    {
        NSRect arrowRect = [self arrowRectForBounds:cellFrame];
        if (NSPointInRect(point, arrowRect))
        {
            if ([arrowTarget respondsToSelector:arrowAction])
                [arrowTarget performSelector:arrowAction withObject:controlView];
            if ([controlView respondsToSelector:@selector(ignoreEventForEdition:)])
                [(id)controlView ignoreEventForEdition:event];
            return YES;
        }
    }
    if (buttonImageName != nil)
    {
        NSRect buttonRect = [self buttonRectForBounds:cellFrame];
        if (NSPointInRect(point, buttonRect))
        {
            if ([buttonTarget respondsToSelector:buttonAction])
                [buttonTarget performSelector:buttonAction withObject:controlView];
            if ([controlView respondsToSelector:@selector(ignoreEventForEdition:)])
                [(id)controlView ignoreEventForEdition:event];
            return YES;
        }
    }

    return [super trackMouse:event inRect:cellFrame ofView:controlView untilMouseUp:untilMouseUp];
}
@end
