/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGScheduleTable.h"
#import "MGTableView.h"
#import "MGSchedulePrint.h"

@implementation MGScheduleTable
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyScheduleTable" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    return self;
}

/* Overrides */
- (PyScheduleTable *)py
{
    return (PyScheduleTable *)py;
}

- (NSView *)viewToPrint
{
    return [[[MGSchedulePrint alloc] initWithPyParent:py tableView:[self tableView]] autorelease];
}

/* Delegate */
- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [[self py] editItem];
    return YES;
}

- (void)tableViewWasDoubleClicked:(MGTableView *)tableView
{
    [[self py] editItem];
}
@end