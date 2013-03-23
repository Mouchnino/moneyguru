/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyScheduleView.h"
#import "MGBaseView.h"
#import "MGTableView.h"
#import "MGScheduleTable.h"

@interface MGScheduleView : MGBaseView
{
    MGTableView *tableView;
    MGScheduleTable *scheduleTable;
}
- (id)initWithPyRef:(PyObject *)aPyRef;

- (PyScheduleView *)model;
@end