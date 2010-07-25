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

- (void)initializeColumns:(MGColumnDef *)columns
{
    for (NSTableColumn *c in [[[tableView tableColumns] copy] autorelease]) {
        [tableView removeTableColumn:c];
    }
    NSUserDefaults *udc = [NSUserDefaultsController sharedUserDefaultsController];
    MGColumnDef *cdef = columns;
    while (cdef->attrname != nil) {
        NSTableColumn *c = [[[NSTableColumn alloc] initWithIdentifier:cdef->attrname] autorelease];
        NSString *title = NSLocalizedStringFromTable(cdef->title, @"columns", @"");
        [[c headerCell] setStringValue:title];
        [c setSortDescriptorPrototype:[[[NSSortDescriptor alloc] initWithKey:cdef->attrname ascending:YES] autorelease]];
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
