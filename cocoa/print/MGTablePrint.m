/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTablePrint.h"
#import "MGConst.h"
#import "MGGraphic.h"
#import "Utils.h"
#import <math.h>

#define CELL_PADDING 8

static NSParagraphStyle* makeParagraphRightAligned(NSParagraphStyle *p)
{
    if (p == nil) {
        p = [NSParagraphStyle defaultParagraphStyle];
    }
    NSMutableParagraphStyle *mp = [p mutableCopy];
    [mp setAlignment:NSRightTextAlignment];
    return [mp autorelease];
}

static NSDictionary* makeAttributesRightAligned(NSDictionary *attrs)
{
    NSParagraphStyle *p = [attrs objectForKey:NSParagraphStyleAttributeName];
    NSMutableDictionary *result = [attrs mutableCopy];
    [result setObject:makeParagraphRightAligned(p) forKey:NSParagraphStyleAttributeName];
    return [result autorelease];
}

@implementation MGTablePrint
- (id)initWithPyParent:(id)pyParent tableView:(NSTableView *)aTableView
{
    self = [super initWithPyParent:pyParent];
    tableView = [aTableView retain];
    
    rowFont = [[NSFont systemFontOfSize:fontSize] retain];
    rowAttributes = [[NSDictionary dictionaryWithObjectsAndKeys:rowFont, NSFontAttributeName,
        [NSColor blackColor], NSForegroundColorAttributeName, nil] retain];
    rowTextHeight = [@"foo" sizeWithAttributes:rowAttributes].height;
    
    cellData = [[NSMutableArray array] retain];
    columnWidths = [[NSMutableArray array] retain];
    rowHeights = [[NSMutableArray array] retain];
    visibleColumns = [[NSMutableArray array] retain];
    
    return self;
}

- (void)dealloc
{
    [tableView release];
    [rowFont release];
    [rowAttributes release];
    [cellData release];
    [columnWidths release];
    [rowHeights release];
    [visibleColumns release];
    [super dealloc];
}

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [super setUpWithPrintInfo:pi];
    
    columnHeaderY = headerHeight;
    // Add the height of the column header to the header height
    headerHeight += headerTextHeight + 6;
    
    typicalRowHeight = rowTextHeight + 2;
    rowCount = [tableView numberOfRows];
    
    // Process only vivible columns
    [visibleColumns removeAllObjects];
    for (NSTableColumn *c in [tableView tableColumns]) {
        if (![c isHidden])
            [visibleColumns addObject:c];
    }
    
    // Fetch all data
    [cellData removeAllObjects];
    [rowHeights removeAllObjects];
    for (NSInteger i=0; i<rowCount; i++)
    {
        NSMutableArray *row = [NSMutableArray array];
        for (NSTableColumn *c in visibleColumns) {
            NSString *value = [self objectValueForTableColumn:c row:i];
            if (value == nil)
                value = @"";
            [row addObject:value];
        }
        [cellData addObject:row];
        [rowHeights addObject:f2n([self heightForRow:i])];
    }
    
    // Figure out the page count
    pageCount = 1;
    CGFloat bottomY = headerHeight;
    for (NSNumber *n in rowHeights) {
        CGFloat h = n2f(n);
        if (h + bottomY > pageHeight) {
            pageCount++;
            bottomY = headerHeight;
        }
        bottomY += h;
    }
    lastRowYOnLastPage = bottomY;

    // Compute each column's max and avg width according to data
    NSArray *cantResize = [self unresizableColumns];
    NSMutableArray *maxWidths = [NSMutableArray array];
    NSMutableArray *avgWidths = [NSMutableArray array];
    [columnWidths removeAllObjects];
    CGFloat totalWidths = 0;
    CGFloat removableWidth = 0; // difference between max and avg for columns going over the threshold
    for (NSInteger i=0; i<[visibleColumns count]; i++)
    {
        NSTableColumn *c = [visibleColumns objectAtIndex:i];
        NSString *headerTitle = [[c headerCell] stringValue];
        CGFloat maxWidth = [headerTitle sizeWithAttributes:headerAttributes].width + (CELL_PADDING*2);
        CGFloat totalWidth = 0;
        for (NSInteger j=0; j<rowCount; j++)
        {
            NSArray *row = [cellData objectAtIndex:j];
            id value = [row objectAtIndex:i];
            NSString *stringValue = value;
            CGFloat width = 0;
            if (![stringValue isEqualTo:@""])
                width = [stringValue sizeWithAttributes:rowAttributes].width + CELL_PADDING;
            width += [self indentForTableColumn:c row:j];
            maxWidth = MAX(maxWidth, width);
            totalWidth += width;
        }
        CGFloat avgWidth = 0;
        if (maxWidth == 0) // A column with no value. keep the NSTableColumn's width
        {
            maxWidth = [c width];
            avgWidth = [c width];
        }
        else
            avgWidth = totalWidth / rowCount;
        [maxWidths addObject:f2n(maxWidth)];
        [avgWidths addObject:f2n(avgWidth)];
        [columnWidths addObject:f2n(maxWidth)];
        totalWidths += maxWidth;
        if (![cantResize containsObject:[c identifier]])
            removableWidth += maxWidth - avgWidth;
    }
    
    // Fitting column widths to the page width
    if (totalWidths > pageWidth)
    {
        CGFloat togain = totalWidths - pageWidth;
        for (NSInteger i=0; i<[maxWidths count]; i++)
        {
            NSTableColumn *c = [visibleColumns objectAtIndex:i];
            CGFloat maxWidth = n2f([maxWidths objectAtIndex:i]);
            CGFloat avgWidth = n2f([avgWidths objectAtIndex:i]);
            CGFloat diff = maxWidth - avgWidth;
            if (![cantResize containsObject:[c identifier]])
            {
                // This column has to be trimmed. Use removableWidth to figure out our share of the
                // width to remove
                CGFloat proportion = diff / removableWidth;
                CGFloat toremove = togain * proportion;
                [columnWidths replaceObjectAtIndex:i withObject:f2n(maxWidth-toremove)];
            }
        }
    }
}

- (id)objectValueForTableColumn:(NSTableColumn *)aColumn row:(NSInteger)aRow
{
    id d = [tableView delegate];
    return [d tableView:tableView objectValueForTableColumn:aColumn row:aRow];
}

- (void)willDisplayCell:(NSCell *)aCell forTableColumn:(NSTableColumn *)aColumn row:(NSInteger)aRow
{
    id d = [tableView delegate];
    if ([d respondsToSelector:@selector(tableView:willDisplayCell:forTableColumn:row:)])
        [d tableView:tableView willDisplayCell:aCell forTableColumn:aColumn row:aRow];
}

- (CGFloat)indentForTableColumn:(NSTableColumn *)aColumn row:(NSInteger)aRow
{
    return 0;
}

- (CGFloat)heightForRow:(NSInteger)aRow
{
    return typicalRowHeight;
}

- (NSArray *)unresizableColumns
{
    return [NSArray array];
}

- (void)drawRow:(NSInteger)aRow inRect:(NSRect)aRect
{
    NSArray *row = [cellData objectAtIndex:aRow];
    CGFloat cumulativeHeaderX = NSMinX(aRect);
    for (NSInteger i=0; i<[visibleColumns count]; i++)
    {
        NSTableColumn *c = [visibleColumns objectAtIndex:i];
        NSString *valueToDraw = [row objectAtIndex:i];
        CGFloat colWidth = n2f([columnWidths objectAtIndex:i]);
        CGFloat indent = [self indentForTableColumn:c row:aRow];
        CGFloat cellX = cumulativeHeaderX + indent;
        CGFloat cellWidth = colWidth - indent;
        NSRect drawRect = NSMakeRect(cellX, NSMinY(aRect), cellWidth, rowTextHeight);
        NSCell *cell = [c dataCellForRow:aRow];
        [cell setFont:rowFont];
        [cell setObjectValue:valueToDraw];
        [self willDisplayCell:cell forTableColumn:c row:aRow];
        [cell drawInteriorWithFrame:drawRect inView:self];
        cumulativeHeaderX += colWidth;
    }
}

- (BOOL)isFlipped
{
    // NSTableView is flipped, so if we want to leverage NSCell used in them and having custom
    // drawing, we should also use flipped coordinates.
    return YES;
}

- (CGFloat)columnsTotalWidth
{
    CGFloat result = 0.0;
    for (NSNumber *n in columnWidths)
        result += n2f(n);
    return result;
}

// Return the number of pages available for printing
- (BOOL)knowsPageRange:(NSRangePointer)range
{
    range->location = 1;
    range->length = pageCount;
    return YES;
}
 
// Return the drawing rectangle for a particular page number
- (NSRect)rectForPage:(NSInteger)page
{
    return [self bounds];
}

- (void)drawRect:(NSRect)rect
{
    [super drawRect:rect];
    NSInteger pageNumber = [[NSPrintOperation currentOperation] currentPage];
    CGFloat headerY = columnHeaderY;
    CGFloat lineY = headerY + headerTextHeight + 2;
    NSInteger page = 1;
    NSInteger startRow = pageNumber == 1 ? 0 : -1;
    NSInteger endRow = -1;
    CGFloat bottomY = headerHeight;
    for (NSInteger i=0; i<[rowHeights count]; i++)
    {
        CGFloat h = n2f([rowHeights objectAtIndex:i]);
        if (h + bottomY > pageHeight)
        {
            if (page == pageNumber)
            {
                endRow = i - 1;
                break;
            }
            page++;
            bottomY = headerHeight;
            if (page == pageNumber)
                startRow = i;
        }
        bottomY += h;
    }
    if (endRow < 0) // we're on the last page
        endRow = rowCount - 1;
    
    // Header Line
    [[NSColor blackColor] setStroke];
    SIMPLE_LINE(0, lineY, pageWidth, lineY, 2);
    
    if (startRow < 0) // a page without rows
        return;
    
    // Header Columns
    CGFloat cumulativeHeaderX = 0;
    for (NSInteger i=0; i<[visibleColumns count]; i++)
    {
        NSTableColumn *c = [visibleColumns objectAtIndex:i];
        CGFloat colWidth = n2f([columnWidths objectAtIndex:i]);
        NSString *headerToDraw = [[c headerCell] stringValue];
        NSRect drawRect = NSMakeRect(cumulativeHeaderX, headerY, colWidth, headerTextHeight);
        NSDictionary *attrs = headerAttributes;
        if ([[c headerCell] alignment] == NSRightTextAlignment) {
            attrs = makeAttributesRightAligned(attrs);
        }
        [headerToDraw drawInRect:drawRect withAttributes:attrs];
        cumulativeHeaderX += colWidth;
    }
    
    // Rows
    CGFloat rowY = headerHeight;
    for (NSInteger i=startRow; i<=endRow; i++)
    {
        CGFloat rowHeight = n2f([rowHeights objectAtIndex:i]);
        NSRect drawRect = NSMakeRect(0, rowY, pageWidth, rowHeight);
        [self drawRow:i inRect:drawRect];
        rowY += rowHeight;
    }
}
@end