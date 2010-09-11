/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGeneralLedgerPrint.h"
#import "MGConst.h"
#import "MGGraphic.h"

#define ACCOUNTROW_XPADDING 8
#define ACCOUNTROW_LINEWIDTH 2

@implementation MGGeneralLedgerPrint
- (id)initWithPyParent:(id)pyParent tableView:(NSTableView *)aTableView
{
    self = [super initWithPyParent:pyParent tableView:aTableView];
    accountRowIndexes = [[NSMutableIndexSet indexSet] retain];
    return self;
}

- (void)dealloc
{
    [accountRowIndexes release];
    [super dealloc];
}

+ (NSString *)pyClassName
{
    return @"PyEntryPrint";
}

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [accountRowIndexes removeAllIndexes];
    [super setUpWithPrintInfo:pi];
}

- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"status",@"date",@"reconciliation_date",@"balance",@"debit",
        @"credit",nil];
}

- (NSArray *)accountColumnNames
{
    return [NSArray arrayWithObjects:@"transfer",nil];
}

- (NSInteger)splitCountThreshold
{
    return 3;
}

- (NSArray *)fetchDataForRow:(NSInteger)rowIndex
{
    if ([[tableView delegate] tableView:tableView isGroupRow:rowIndex]) {
        [accountRowIndexes addIndex:rowIndex];
        NSMutableArray *row = [NSMutableArray array];
        // we don't care about the column because account rows always return account name regardless
        [row addObject:[self objectValueForTableColumn:nil row:rowIndex]];
        for (NSInteger i=0; i<[visibleColumns count]-1; i++) {
            [row addObject:@""];
        }
        return row;
    }
    else {
        return [super fetchDataForRow:rowIndex];
    }
}

- (BOOL)shouldComputeRowWidths:(NSInteger)row
{
    return ![accountRowIndexes containsIndex:row];
}

- (void)drawRow:(NSInteger)aRow inRect:(NSRect)r
{
    if ([accountRowIndexes containsIndex:aRow]) {
        NSColor *bgColor = [NSColor lightGrayColor];
        NSColor *lineColor = [NSColor blackColor];
        [bgColor setFill];
        [lineColor setStroke];
	    [NSBezierPath fillRect:r];
        SIMPLE_LINE(NSMinX(r), NSMinY(r)+1, NSMaxX(r), NSMinY(r)+1, ACCOUNTROW_LINEWIDTH);
        r.origin.x += ACCOUNTROW_XPADDING;
        r.size.width -= ACCOUNTROW_XPADDING;
        r.origin.y += ACCOUNTROW_LINEWIDTH;
        NSArray *row = [cellData objectAtIndex:aRow];
        NSString *accountName = [row objectAtIndex:0];
        [accountName drawInRect:r withAttributes:rowAttributes];
    }
    else {
        [super drawRow:aRow inRect:r];
    }
}
@end