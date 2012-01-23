/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGeneralLedgerTableView.h"
#import "MGGraphic.h"

#define ACCOUNTROW_XPADDING 8
#define ACCOUNTROW_LINEWIDTH 2

@implementation MGGeneralLedgerTableView
- (void)drawRow:(NSInteger)rowIndex clipRect:(NSRect)clipRect
{
    BOOL isGroup = [[self delegate] tableView:self isGroupRow:rowIndex];
    if (isGroup) {
        NSRect r = [self rectOfRow:rowIndex];
        NSColor *bgColor = [NSColor lightGrayColor];
        NSColor *textColor = [NSColor controlTextColor];
        NSColor *lineColor = [NSColor blackColor];
        if ([self isRowSelected:rowIndex]) {
            bgColor = [NSColor alternateSelectedControlColor];
            textColor = [NSColor alternateSelectedControlTextColor];
        }
        [bgColor setFill];
        [lineColor setStroke];
	    [NSBezierPath fillRect:r];
        SIMPLE_LINE(NSMinX(r), NSMinY(r)+1, NSMaxX(r), NSMinY(r)+1, ACCOUNTROW_LINEWIDTH);
        NSFont *font = [NSFont boldSystemFontOfSize:[self rowHeight]-4];
        NSDictionary *attrs = [NSDictionary dictionaryWithObjectsAndKeys:font, NSFontAttributeName,
            textColor, NSForegroundColorAttributeName, nil];
        r.origin.x += ACCOUNTROW_XPADDING;
        r.size.width -= ACCOUNTROW_XPADDING;
        r.origin.y += ACCOUNTROW_LINEWIDTH;
        // We pass a nil column because the datasource always returns the account namefor account rows anyway.
        NSString *accountName = [[self dataSource] tableView:self objectValueForTableColumn:nil row:rowIndex];
        [accountName drawInRect:r withAttributes:attrs];
    }
    else {
        [super drawRow:rowIndex clipRect:clipRect];
    }
}

- (void)drawGridInClipRect:(NSRect)clipRect
{
    /* What we want here is to never draw grid lines over an account row, so we split clipRect
       in multiple sub rectangle that don't include account rows.
     */
    NSRange affectedRows = [self rowsInRect:clipRect];
    NSInteger groupRow = -1;
    NSUInteger start = affectedRows.location;
    NSUInteger stop = start + affectedRows.length;
    for (NSInteger i=start; i<stop; i++) {
        if ([[self delegate] tableView:self isGroupRow:i]) {
            groupRow = i;
            break;
        }
    }
    if (groupRow >= 0) {
        NSRect groupRect = [self rectOfRow:groupRow];
        NSRect top = clipRect;
        NSRect bottom = clipRect;
        top.size.height = (NSMinY(groupRect) - NSMinY(clipRect)) - 1;
        bottom.origin.y = NSMaxY(groupRect) + 1;
        bottom.size.height = NSMaxY(clipRect) - NSMinY(bottom);
        if (!NSIsEmptyRect(top)) {
            [self drawGridInClipRect:top];
        }
        if (!NSIsEmptyRect(bottom) && (NSMinY(bottom) < NSMaxY(clipRect))) {
            [self drawGridInClipRect:bottom];
        }
    }
    else {
        [super drawGridInClipRect:clipRect];
    }
}
@end