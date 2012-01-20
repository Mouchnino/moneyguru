/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGPanel2.h"
#import "PyCustomDateRangePanel.h"

@class MGMainWindowController;

@interface MGCustomDateRangePanel : MGPanel2 {
    IBOutlet NSTextField *startDateField;
    IBOutlet NSTextField *endDateField;
    IBOutlet NSPopUpButton *slotIndexSelector;
    IBOutlet NSTextField *slotNameField;
}
- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyCustomDateRangePanel *)model;
@end