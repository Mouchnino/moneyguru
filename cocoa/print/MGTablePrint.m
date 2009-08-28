/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTablePrint.h"
#import "MGConst.h"
#import "MGGraphic.h"
#import "Utils.h"
#import <math.h>

#define CELL_PADDING 4

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
    
    // Fetch all data
    [cellData removeAllObjects];
    [rowHeights removeAllObjects];
    for (int i=0; i<rowCount; i++)
    {
        NSMutableArray *row = [NSMutableArray array];
        NSEnumerator *e = [[tableView tableColumns] objectEnumerator];
        NSTableColumn *c;
        while (c = [e nextObject])
        {
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
    float bottomY = headerHeight;
    NSEnumerator *e = [rowHeights objectEnumerator];
    NSNumber *n;
    while (n = [e nextObject])
    {
        float h = n2f(n);
        if (h + bottomY > pageHeight)
        {
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
    float totalWidths = 0;
    float removableWidth = 0; // difference between max and avg for columns going over the threshold
    for (int i=0; i<[[tableView tableColumns] count]; i++)
    {
        NSTableColumn *c = [[tableView tableColumns] objectAtIndex:i];
        NSString *headerTitle = [[c headerCell] stringValue];
        float maxWidth = [headerTitle sizeWithAttributes:headerAttributes].width;
        float totalWidth = 0;
        for (int j=0; j<rowCount; j++)
        {
            NSArray *row = [cellData objectAtIndex:j];
            id value = [row objectAtIndex:i];
            NSString *stringValue = value;
            float width = 0;
            if (![stringValue isEqualTo:@""])
                width = [stringValue sizeWithAttributes:rowAttributes].width + CELL_PADDING;
            width += [self indentForTableColumn:c row:j];
            maxWidth = MAX(maxWidth, width);
            totalWidth += width;
        }
        float avgWidth = 0;
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
        float togain = totalWidths - pageWidth;
        for (int i=0; i<[maxWidths count]; i++)
        {
            NSTableColumn *c = [[tableView tableColumns] objectAtIndex:i];
            float maxWidth = n2f([maxWidths objectAtIndex:i]);
            float avgWidth = n2f([avgWidths objectAtIndex:i]);
            float diff = maxWidth - avgWidth;
            if (![cantResize containsObject:[c identifier]])
            {
                // This column has to be trimmed. Use removableWidth to figure out our share of the
                // width to remove
                float proportion = diff / removableWidth;
                float toremove = togain * proportion;
                [columnWidths replaceObjectAtIndex:i withObject:f2n(maxWidth-toremove)];
            }
        }
    }
}

- (id)objectValueForTableColumn:(NSTableColumn *)aColumn row:(int)aRow
{
    id d = [tableView delegate];
    return [d tableView:tableView objectValueForTableColumn:aColumn row:aRow];
}

- (void)willDisplayCell:(NSCell *)aCell forTableColumn:(NSTableColumn *)aColumn row:(int)aRow
{
    id d = [tableView delegate];
    if ([d respondsToSelector:@selector(tableView:willDisplayCell:forTableColumn:row:)])
        [d tableView:tableView willDisplayCell:aCell forTableColumn:aColumn row:aRow];
}

- (float)indentForTableColumn:(NSTableColumn *)aColumn row:(int)aRow
{
    return 0;
}

- (float)heightForRow:(int)aRow
{
    return typicalRowHeight;
}

- (NSArray *)unresizableColumns
{
    return [NSArray array];
}

- (void)drawRow:(int)aRow inRect:(NSRect)aRect
{
    NSArray *row = [cellData objectAtIndex:aRow];
    float cumulativeHeaderX = NSMinX(aRect);
    for (int i=0; i<[[tableView tableColumns] count]; i++)
    {
        NSTableColumn *c = [[tableView tableColumns] objectAtIndex:i];
        NSString *valueToDraw = [row objectAtIndex:i];
        float colWidth = n2f([columnWidths objectAtIndex:i]);
        float indent = [self indentForTableColumn:c row:aRow];
        float cellX = cumulativeHeaderX + indent;
        float cellWidth = colWidth - indent;
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

- (float)columnsTotalWidth
{
    float result = 0.0;
    NSEnumerator *e = [columnWidths objectEnumerator];
    NSNumber *n;
    while (n = [e nextObject])
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
- (NSRect)rectForPage:(int)page
{
    return [self bounds];
}

- (void)drawRect:(NSRect)rect
{
    [super drawRect:rect];
    int pageNumber = [[NSPrintOperation currentOperation] currentPage];
    float headerY = columnHeaderY;
    float lineY = headerY + headerTextHeight + 2;
    int page = 1;
    int startRow = pageNumber == 1 ? 0 : -1;
    int endRow = -1;
    float bottomY = headerHeight;
    for (int i=0; i<[rowHeights count]; i++)
    {
        float h = n2f([rowHeights objectAtIndex:i]);
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
    float cumulativeHeaderX = 0;
    for (int i=0; i<[[tableView tableColumns] count]; i++)
    {
        NSTableColumn *c = [[tableView tableColumns] objectAtIndex:i];
        float colWidth = n2f([columnWidths objectAtIndex:i]);
        NSString *headerToDraw = [[c headerCell] stringValue];
        NSRect drawRect = NSMakeRect(cumulativeHeaderX, headerY, colWidth, headerTextHeight);
        [headerToDraw drawInRect:drawRect withAttributes:headerAttributes];
        cumulativeHeaderX += colWidth;
    }
    
    // Rows
    float rowY = headerHeight;
    for (int i=startRow; i<=endRow; i++)
    {
        float rowHeight = n2f([rowHeights objectAtIndex:i]);
        NSRect drawRect = NSMakeRect(0, rowY, pageWidth, rowHeight);
        [self drawRow:i inRect:drawRect];
        rowY += rowHeight;
    }
}
@end