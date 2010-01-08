/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGScheduleView.h"

@implementation MGScheduleView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    scheduleTable = [[MGScheduleTable alloc] initWithDocument:aDocument view:tableView];
    return self;
}
        
- (void)dealloc
{
    [scheduleTable release];
    [super dealloc];
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
    [scheduleTable connect];
}

- (void)disconnect
{
    [scheduleTable disconnect];
}

- (MGScheduleTable *)scheduleTable
{
    return scheduleTable;
}
@end