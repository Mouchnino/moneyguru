/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGImportTable.h"
#import "Utils.h"
#import "MGConst.h"

@implementation MGImportTable

- (id)initWithImportWindow:(PyImportWindow *)aWindow view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyImportTable" pyParent:aWindow view:aTableView];
    [aTableView registerForDraggedTypes:[NSArray arrayWithObject:MGImportEntryPasteboardType]];
    return self;
}

- (PyImportTable *)py
{
    return (PyImportTable *)py;
}

- (void)tableView:(NSTableView *)tableView willDisplayCell:(id)aCell forTableColumn:(NSTableColumn *)column row:(int)row
{
    // Cocoa's typeselect mechanism can call us with an out-of-range row
    if (row >= [[self py] numberOfRows])
    {
        return;
    }
    NSString *colname = [column identifier];
    if ([colname isEqualToString:@"will_import"])
    {
        BOOL canEdit = [[self py] canEditColumn:@"will_import" atRow:row];
        [aCell setEnabled:canEdit];
        return;
    }
}

- (BOOL)tableView:(NSTableView *)tv writeRowsWithIndexes:(NSIndexSet *)rowIndexes toPasteboard:(NSPasteboard*)pboard
{
    NSData *data = [NSKeyedArchiver archivedDataWithRootObject:rowIndexes];
    [pboard declareTypes:[NSArray arrayWithObject:MGImportEntryPasteboardType] owner:self];
    [pboard setData:data forType:MGImportEntryPasteboardType];
    return YES;
}

- (NSDragOperation)tableView:(NSTableView*)tv validateDrop:(id <NSDraggingInfo>)info proposedRow:(int)row 
       proposedDropOperation:(NSTableViewDropOperation)op
{
    if (op == NSTableViewDropOn)
    {
        NSPasteboard* pboard = [info draggingPasteboard];
        NSData* rowData = [pboard dataForType:MGImportEntryPasteboardType];
        NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
        int source = [rowIndexes firstIndex];
        if ([[self py] canBindRow:source to:row])
        {
            return NSDragOperationMove;
        }
    }
    return NSDragOperationNone;
}

- (BOOL)tableView:(NSTableView *)aTableView acceptDrop:(id <NSDraggingInfo>)info
              row:(int)row dropOperation:(NSTableViewDropOperation)operation
{
    NSPasteboard* pboard = [info draggingPasteboard];
    NSData* rowData = [pboard dataForType:MGImportEntryPasteboardType];
    NSIndexSet* rowIndexes = [NSKeyedUnarchiver unarchiveObjectWithData:rowData];
    int source = [rowIndexes firstIndex];
    [[self py] bindRow:source to:row];
    return YES;
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self py] toggleImportStatus];
    return YES;
}

@end