/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGColumns.h"
#import "Utils.h"
#import "PyTableWithColumns.h"

@implementation MGColumns
- (id)initWithPy:(id)aPy tableView:(NSTableView *)aTableView
{
    self = [super init];
    py = [aPy retain];
    tableView = [aTableView retain];
    isRestoring = NO;
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(columnMoved:)
        name:NSTableViewColumnDidMoveNotification object:aTableView];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(columnMoved:)
        name:NSOutlineViewColumnDidMoveNotification object:aTableView];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(columnResized:)
        name:NSTableViewColumnDidResizeNotification object:aTableView];
    [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(columnResized:)
        name:NSOutlineViewColumnDidResizeNotification object:aTableView];
    return self;
}

- (void)dealloc
{
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [py release];
    [tableView release];
    [super dealloc];
}

/*
    It is assumed, when this method is used, that the table/outline is empty *OR* that it is not
    defined in the column list.
    
    Special note about NSOutlineView. You can use MGColumns on outline views, but you be aware that
    the "main" column (the one having the tree disclosure buttons) cannot be removed. Therefore,
    it has to be defined in the XIB and it must *not* be in column defs.
*/
- (void)initializeColumns:(MGColumnDef *)columns
{
    /* Translate the title of columns (needed for outlines) present already */
    for (NSTableColumn *c in [tableView tableColumns]) {
        NSString *title = NSLocalizedStringFromTable([[c headerCell] stringValue], @"columns", @"");
        [[c headerCell] setStringValue:title];
    }
    NSUserDefaults *udc = [NSUserDefaultsController sharedUserDefaultsController];
    MGColumnDef *cdef = columns;
    while (cdef->attrname != nil) {
        if ([tableView tableColumnWithIdentifier:cdef->attrname] != nil) {
            cdef++;
            continue;
        }
        NSTableColumn *c = [[[NSTableColumn alloc] initWithIdentifier:cdef->attrname] autorelease];
        NSString *title = NSLocalizedStringFromTable(cdef->title, @"columns", @"");
        [[c headerCell] setStringValue:title];
        if (cdef->sortable) {
            NSSortDescriptor *d = [[[NSSortDescriptor alloc] initWithKey:cdef->attrname ascending:YES] autorelease];
            [c setSortDescriptorPrototype:d];
        }
        [c setWidth:cdef->defaultWidth];
        [c setMinWidth:cdef->minWidth];
        NSUInteger maxWidth = cdef->maxWidth;
        if (maxWidth == 0) {
            maxWidth = 0xffffff;
        }
        [c setMaxWidth:maxWidth];
        if (cdef->cellClass != nil) {
            id cell = [[[cdef->cellClass alloc] initTextCell:@""] autorelease];
            [cell setEditable:YES];
            [c setDataCell:cell];
        }
        [c bind:@"fontSize" toObject:udc withKeyPath:@"values.TableFontSize" options:nil];
        [tableView addTableColumn:c];
        cdef++;
    }
}

/* Call this after initializeColumns to query the core and see if column data has been restored from
   preferences. If there is, we apply these changes.
*/
- (void)restoreColumns
{
    isRestoring = YES;
    NSArray *columnOrder = [py columnNamesInOrder];
    for (NSInteger i=0; i<[columnOrder count]; i++) {
        NSString *colName = [columnOrder objectAtIndex:i];
        NSInteger index = [tableView columnWithIdentifier:colName];
        if ((index != -1) && (index != i)) {
            [tableView moveColumn:index toColumn:i];
        }
    }
    for (NSTableColumn *c in [tableView tableColumns]) {
        NSInteger width = [py columnWidth:[c identifier]];
        if (width > 0) {
            [c setWidth:width];
        }
    }
    isRestoring = NO;
}

/* Notifications */
- (void)columnMoved:(NSNotification *)notification
{
    /* We only get this call after the move. Although there's "NSOldColumn" and "NSNewColumn",
       the old index is irrelevant since we have to find the moved column's name.
    */
    if (isRestoring) {
        return;
    }
    NSInteger index = n2i([[notification userInfo] objectForKey:@"NSNewColumn"]);
    NSTableColumn *c = [[tableView tableColumns] objectAtIndex:index];
    NSString *colName = [c identifier];
    [py moveColumn:colName toIndex:index];
}

- (void)columnResized:(NSNotification *)notification
{
    if (isRestoring) {
        return;
    }
    NSTableColumn *c = [[notification userInfo] objectForKey:@"NSTableColumn"];
    [py resizeColumn:[c identifier] toWidth:[c width]];
}
@end
