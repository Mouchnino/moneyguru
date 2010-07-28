/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGColumns.h"
#import "Utils.h"
#import "MGTableView.h"

@implementation MGColumns
- (id)initWithPyParent:(id)aPyParent tableView:(NSTableView *)aTableView
{
    self = [super initWithPyClassName:@"PyColumns" pyParent:(id)aPyParent];
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
    [tableView release];
    [super dealloc];
}

- (PyColumns *)py
{
    return (PyColumns *)py;
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
    NSArray *columnOrder = [[self py] columnNamesInOrder];
    for (NSInteger i=0; i<[columnOrder count]; i++) {
        NSString *colName = [columnOrder objectAtIndex:i];
        NSInteger index = [tableView columnWithIdentifier:colName];
        if ((index != -1) && (index != i)) {
            [tableView moveColumn:index toColumn:i];
        }
    }
    for (NSTableColumn *c in [tableView tableColumns]) {
        NSInteger width = [[self py] columnWidth:[c identifier]];
        if (width > 0) {
            [c setWidth:width];
        }
        BOOL isVisible = [[self py] columnIsVisible:[c identifier]];
        [c setHidden:!isVisible];
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
    [[self py] moveColumn:colName toIndex:index];
}

- (void)columnResized:(NSNotification *)notification
{
    if (isRestoring) {
        return;
    }
    NSTableColumn *c = [[notification userInfo] objectForKey:@"NSTableColumn"];
    [[self py] resizeColumn:[c identifier] toWidth:[c width]];
}

/* Python --> Cocoa */
- (void)setColumn:(NSString *)colname visible:(BOOL)visible
{
    NSTableColumn *col = [tableView tableColumnWithIdentifier:colname];
    if (col == nil)
        return;
    if ([col isHidden] == !visible)
        return;
    if ([tableView respondsToSelector:@selector(stopEditing)]) {
        [(id)tableView stopEditing];
    }
    [col setHidden:!visible];
}
@end
