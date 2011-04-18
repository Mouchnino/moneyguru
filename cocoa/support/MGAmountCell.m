/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAmountCell.h"

@implementation MGAmountCell

- (void)setSubtotal:(BOOL)value
{
    subtotal = value;
}

- (void)setTotal:(BOOL)value
{
    total = value;
}

/* NSCopying (we implement it because, apparently, NSTableView likes to copy cells) */

- (id)copyWithZone:(NSZone *)zone
{
    MGAmountCell *result = [super copyWithZone:zone];
    [result setTotal:total];
    [result setSubtotal:subtotal];
    return result;
}

/* NSCell */

- (void)drawInteriorWithFrame:(NSRect)cellFrame inView:(NSView *)controlView
{
    [super drawInteriorWithFrame:cellFrame inView:controlView];

    /* Add total lines if requested */
    if (subtotal)
    {
        [NSBezierPath fillRect:NSMakeRect(NSMinX(cellFrame), NSMaxY(cellFrame), NSWidth(cellFrame), 1)];
    }

    if (total)
    {
        [NSBezierPath fillRect:NSMakeRect(NSMinX(cellFrame), NSMaxY(cellFrame) - 2, NSWidth(cellFrame), 1)];
        [NSBezierPath fillRect:NSMakeRect(NSMinX(cellFrame), NSMaxY(cellFrame), NSWidth(cellFrame), 1)];
    }
}

@end
