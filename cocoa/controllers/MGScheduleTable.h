/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGTableView.h"
#import "MGDocument.h"
#import "PyScheduleTable.h"
#import "MGTable.h"
#import "MGSchedulePanel.h"

@interface MGScheduleTable : MGTable 
{
    MGSchedulePanel *schedulePanel;
}
- (id)initWithDocument:(MGDocument *)aDocument;

/* Public */
- (PyScheduleTable *)py;
- (void)add;
- (void)deleteSelected;
- (void)editSelected;
@end