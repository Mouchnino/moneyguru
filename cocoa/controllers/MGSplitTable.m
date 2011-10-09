/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSplitTable.h"
#import "MGConst.h"
#import "NSEventAdditions.h"

#define MGSplitPasteboardType @"MGSplitPasteboardType"

@implementation MGSplitTable
- (id)initWithPy:(id)aPy view:(MGTableView *)aTableView
{
    self = [super initWithPy:aPy view:aTableView];
    [self initializeColumns];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGSplitPasteboardType]];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"account", @"Account", 90, 40, 0, NO, nil},
        {@"memo", @"Memo #", 44, 10, 0, NO, nil},
        {@"debit", @"Debit", 90, 40, 0, NO, nil},
        {@"credit", @"Credit", 90, 40, 0, NO, nil},
        nil
    };
    [[self columns] initializeColumns:defs];
    NSTableColumn *c = [[self tableView] tableColumnWithIdentifier:@"account"];
    [[c dataCell] setPlaceholderString:TR(@"Unassigned")];
    c = [[self tableView] tableColumnWithIdentifier:@"debit"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
    c = [[self tableView] tableColumnWithIdentifier:@"credit"];
    [[c headerCell] setAlignment:NSRightTextAlignment];
    [[c dataCell] setAlignment:NSRightTextAlignment];
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