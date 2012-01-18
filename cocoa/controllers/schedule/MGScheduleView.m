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
- (id)initWithPy:(id)aPy
{
    self = [super initWithPy:aPy];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    scheduleTable = [[MGScheduleTable alloc] initWithPy:[[self py] table] view:tableView];
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