/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTable.h"
#import "Utils.h"

@implementation MGTable
- (id)initWithPyClassName:(NSString *)aClassName pyParent:(id)aPyParent view:(MGTableView *)aTableView
{
    self = [super initWithPyClassName:aClassName pyParent:aPyParent view:aTableView];
    columns = [[MGColumns alloc] initWithPyParent:[self py] tableView:aTableView];
    return self;
}

- (void)dealloc
{
    [columns release];
    [super dealloc];
}

/* MGTableView delegate */
- (NSIndexSet *)selectedIndexes
{
    return [Utils array2IndexSet:[[self py] selectedRows]];
}

/* Public */
- (PyTable *)py
{
    return (PyTable *)py;
}

- (MGTableView *)tableView
{
    return (MGTableView *)tableView;
}

- (MGColumns *)columns
{
    return columns;
}
@end
