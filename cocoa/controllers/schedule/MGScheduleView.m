/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGScheduleView.h"
#import "MGUtils.h"

@implementation MGScheduleView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    scheduleTable = [[MGScheduleTable alloc] initWithDocument:aDocument view:tableView];
    NSArray *children = [NSArray arrayWithObjects:[scheduleTable py], nil];
    Class pyClass = [MGUtils classNamed:@"PyScheduleView"];
    py = [[pyClass alloc] initWithCocoa:self pyParent:[aDocument py] children:children];
    return self;
}
        
- (void)dealloc
{
    [py release];
    [scheduleTable release];
    [super dealloc];
}

- (oneway void)release
{
    if ([self retainCount] == 2)
        [py free];
    [super release];
}

- (PyScheduleView *)py
{
    return (PyScheduleView *)py;
}

- (NSView *)view
{
    return wholeView;
}

- (MGPrintView *)viewToPrint
{
    return [scheduleTable viewToPrint];
}

- (void)connect
{
    [py connect];
}

- (void)disconnect
{
    [py disconnect];
}

- (MGScheduleTable *)scheduleTable
{
    return scheduleTable;
}
@end