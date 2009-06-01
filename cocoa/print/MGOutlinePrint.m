#import "MGOutlinePrint.h"

@implementation MGOutlinePrint
- (id)objectValueForTableColumn:(NSTableColumn *)aColumn row:(int)aRow
{
    NSOutlineView *o = (NSOutlineView *)tableView;
    id d = [o delegate];
    id item = [o itemAtRow:aRow];
    return [d outlineView:o objectValueForTableColumn:aColumn byItem:item];
}

- (void)willDisplayCell:(NSCell *)aCell forTableColumn:(NSTableColumn *)aColumn row:(int)aRow
{
    NSOutlineView *o = (NSOutlineView *)tableView;
    id d = [o delegate];
    id item = [o itemAtRow:aRow];
    [d outlineView:o willDisplayCell:aCell forTableColumn:aColumn item:item];
}

- (float)indentForTableColumn:(NSTableColumn *)aColumn row:(int)aRow
{
    NSOutlineView *o = (NSOutlineView *)tableView;
    if ([[o tableColumns] indexOfObject:aColumn] == 0)
    {
        int level = [o levelForRow:aRow];
        return level * [o indentationPerLevel];
    }
    else
        return 0;
}

@end