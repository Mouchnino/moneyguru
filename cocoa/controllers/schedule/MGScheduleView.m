/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGScheduleView.h"
#import "MGSchedulePrint.h"
#import "Utils.h"

@implementation MGScheduleView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyScheduleView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    scheduleTable = [[MGScheduleTable alloc] initWithPyParent:[self py] view:tableView];
    NSArray *children = [NSArray arrayWithObjects:[scheduleTable py], nil];
    [[self py] setChildren:children];
    return self;
}
        
- (void)dealloc
{
    [scheduleTable release];
    [super dealloc];
}

- (PyScheduleView *)py
{
    return (PyScheduleView *)py;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGSchedulePrint alloc] initWithPyParent:[self py] 
        tableView:[scheduleTable tableView]] autorelease];
}
@end