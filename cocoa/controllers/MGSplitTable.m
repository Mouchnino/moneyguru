/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSplitTable.h"
#import "MGConst.h"
#import "NSEventAdditions.h"
#import "Utils.h"

#define MGSplitPasteboardType @"MGSplitPasteboardType"

@implementation MGSplitTable
- (id)initWithPyRef:(PyObject *)aPyRef tableView:(MGTableView *)aTableView
{
    PySplitTable *m = [[PySplitTable alloc] initWithModel:aPyRef];
    self = [super initWithModel:m tableView:aTableView];
    [m bindCallback:createCallback(@"TableView", self)];
    [m release];
    [self initializeColumns];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGSplitPasteboardType]];
    return self;
}

- (void)initializeColumns
{
    HSColumnDef defs[] = {
        {@"account", 90, 40, 0, NO, nil},
        {@"memo", 44, 10, 0, NO, nil},
        {@"debit", 90, 40, 0, NO, nil},
        {@"credit", 90, 40, 0, NO, nil},
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

- (PySplitTable *)model
{
    return (PySplitTable *)model;
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
    [[self model] moveSplitFromRow:[rowIndexes firstIndex] toRow:row];
    return YES;
}

/* Delegate */
- (BOOL)tableView:(NSTableView *)tableView receivedKeyEvent:(NSEvent *)aEvent
{
    if ([aEvent isDown] && ([[self tableView] selectedRow] == [[self model] numberOfRows]-1)) {
        [[self model] add];
        return YES;
    }
    return NO;
}
@end