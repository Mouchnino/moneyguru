/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGColumns.h"

@implementation MGColumns
- (id)initWithTableView:(NSTableView *)aTableView
{
    self = [super init];
    tableView = [aTableView retain];
    return self;
}

- (void)dealloc
{
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
@end
