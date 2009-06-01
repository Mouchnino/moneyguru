#import "MGEditableTable.h"
#import "Utils.h"

@implementation MGEditableTable

/* Private */

- (void)changeColumns
{
    NSMutableArray *columnNames = [NSMutableArray array];
    NSEnumerator *e = [[[self tableView] tableColumns] objectEnumerator];
    NSTableColumn *col;
    while (col = [e nextObject])
    {
        [columnNames addObject:[col identifier]];
    }
    [[self py] changeColumns:columnNames];
}

/* Data source */

- (void)tableView:(NSTableView *)tableView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column row:(int)row
{
    [[self py] setValue:value forColumn:[column identifier] row:(int)row];
}

/* NSTableView Delegate */

- (BOOL)tableView:(NSTableView *)tableView shouldEditTableColumn:(NSTableColumn *)column row:(int)row
{
    return [[self py] canEditColumn:[column identifier] atRow:row];
}

- (void)tableViewColumnDidMove:(NSNotification *)notification
{
    [self changeColumns];
}

/* MGTableView delegate */

- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView
{
    [[self py] deleteSelectedRows];
    return YES;
}

- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [[self tableView] startEditing];
    return YES;
}

// This is never called on edition cancel (pressing ESC) or stopEditing call
- (void)tableViewDidEndEditing:(MGTableView *)tableView
{
    [[self py] saveEdits];
}

- (void)tableViewCancelsEdition:(MGTableView *)tableView
{
    [[self py] cancelEdits];
}

- (NSString *)autoCompletionForColumn:(NSTableColumn *)column partialWord:(NSString *)partialWord
{
    return [[self py] completeValue:partialWord forAttribute:[column identifier]];
}

- (NSString *)currentValueForColumn:(NSTableColumn *)column
{
    return [[self py] currentCompletion];
}

- (NSString *)nextValueForColumn:(NSTableColumn *)column
{
    return [[self py] nextCompletion];
}

- (NSString *)prevValueForColumn:(NSTableColumn *)column
{
    return [[self py] prevCompletion];
}

/* Public */

- (void)add
{
    [[self py] add];
}

- (void)deleteSelected
{
    [[self py] deleteSelectedRows];
}

- (void)startEditing
{
    [[self tableView] startEditing];
}

- (void)stopEditing
{
    [[self tableView] stopEditing];
}

@end
