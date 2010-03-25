/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSplitTable.h"
#import "NSEventAdditions.h"

#define MGSplitPasteboardType @"MGSplitPasteboardType"

@implementation MGSplitTable
- (id)initWithTransactionPanel:(PyPanel *)aPanel view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PySplitTable" pyParent:aPanel view:aTableView];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGSplitPasteboardType]];
    return self;
}

- (PySplitTable *)py
{
    return (PySplitTable *)py;
}

/* Datasource */
- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:MGSplitPasteboardType] owner:self];
    [pboard setData:data forType:MGSplitPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(NSInteger)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropAbove) {
        return NSDragOperationMove;
    }
    return NSDragOperationNone;
}

- (BOOL)tableView:(NSTableView *)aTableView acceptDrop:(id <NSDraggingInfo>)info
              row:(NSInteger)row dropOperation:(NSTableViewDropOperation)operation
{
    NSPasteboard *pboard = [info draggingPasteboard];
    NSData *rowData = [pboard dataForType:MGSplitPasteboardType];
    NSIndexSet *rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    [[self py] moveSplitFromRow:[rowIndexes firstIndex] toRow:row];
    return YES;
}

/* Delegate */
- (BOOL)tableView:(NSTableView *)tableView receivedKeyEvent:(NSEvent *)aEvent
{
    if ([aEvent isDown] && ([[self tableView] selectedRow] == [[self py] numberOfRows]-1)) {
        [[self py] add];
        return YES;
    }
    return NO;
}
@end