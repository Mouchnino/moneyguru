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

- (BOOL)mouseEvent:(NSEvent *)event inRect:(NSRect)cellFrame ofView:(NSView *)controlView hitRect:(NSRect)targetRect
{
    NSPoint point = [controlView convertPoint:[event locationInWindow] fromView:nil];
    if (NSMouseInRect(point, targetRect, [controlView isFlipped]))
    {
        // We're in the target. Track until mouse is up.
        NSEvent *mouseUpEvent = [[controlView window] nextEventMatchingMask:NSLeftMouseUpMask];
        NSPoint mouseUpPoint = [controlView convertPoint:[mouseUpEvent locationInWindow] fromView:nil];
        // If YES, We're still on the target. Trigger the action.
        return NSMouseInRect(mouseUpPoint, targetRect, [controlView isFlipped]);
    }
    return NO;
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

// Yeah, this whole tracking business is very hacky

- (BOOL)trackMouse:(NSEvent *)event inRect:(NSRect)cellFrame ofView:(NSView *)controlView untilMouseUp:(BOOL)untilMouseUp
{
    if (hasArrow)
    {
        NSRect arrowRect = [self arrowRectForBounds:cellFrame];
        if ([self mouseEvent:event inRect:cellFrame ofView:controlView hitRect:arrowRect])
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
        if ([self mouseEvent:event inRect:cellFrame ofView:controlView hitRect:buttonRect])
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
