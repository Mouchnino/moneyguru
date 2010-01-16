/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGReconciliationCell.h"

@implementation MGReconciliationCell
/* Overrides */

- (void)drawInteriorWithFrame:(NSRect)cellFrame inView:(NSView *)controlView
{
    NSImage *i = nil;
    if (isInFuture)
        i = [NSImage imageNamed:@"forward_32"];
    else if (isInPast)
        i = [NSImage imageNamed:@"backward_32"];
    else if (reconciled)
        i = [NSImage imageNamed:@"check_16"];
    else if (canReconcile)
        [super drawInteriorWithFrame:cellFrame inView:controlView];
    else if (isBudget)
        i = [NSImage imageNamed:@"budget_16"];
    else if (recurrent)
        i = [NSImage imageNamed:@"recurrent_16"];
    
    if (i != nil)
    {
        CGFloat rectSize = MIN(cellFrame.size.width, cellFrame.size.height);
        NSRect drawRect = NSMakeRect(cellFrame.origin.x, cellFrame.origin.y, rectSize, rectSize);
        [i setFlipped:YES];
        [i drawInRect:drawRect fromRect:NSZeroRect operation:NSCompositeSourceOver fraction:1];
    }    
}
/* Public */

- (void)setCanReconcile:(BOOL)aCanReconcile
{
    canReconcile = aCanReconcile;
    [self setEnabled:canReconcile];
}

- (void)setReconciled:(BOOL)aReconciled
{
    reconciled = aReconciled;
}

- (void)setRecurrent:(BOOL)aRecurrent
{
    recurrent = aRecurrent;
}

- (void)setIsBudget:(BOOL)aIsBudget
{
    isBudget = aIsBudget;
}

- (void)setReconciliationPending:(BOOL)aReconciliationPending
{
    [self setIntValue:aReconciliationPending ? 1 : 0];
}

- (void)setIsInFuture:(BOOL)aIsInFuture
{
    isInFuture = aIsInFuture;
}

- (void)setIsInPast:(BOOL)aIsInPast
{
    isInPast = aIsInPast;
}

@end