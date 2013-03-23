/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGCustomDateRangePanel.h"
#import "MGCustomDateRangePanel_UI.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGCustomDateRangePanel

@synthesize startDateField;
@synthesize endDateField;
@synthesize slotIndexSelector;
@synthesize slotNameField;

- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyCustomDateRangePanel *m = [[PyCustomDateRangePanel alloc] initWithModel:[[aParent model] customDateRangePanel]];
    self = [super initWithModel:m parent:aParent];
    [m bindCallback:createCallback(@"PanelView", self)];
    [m release];
    [self setWindow:createMGCustomDateRangePanel_UI(self)];
    return self;
}

- (PyCustomDateRangePanel *)model
{
    return (PyCustomDateRangePanel *)model;
}

/* Override */
- (BOOL)isFieldDateField:(id)aField
{
    return (aField == startDateField) || (aField == endDateField);
}

- (NSResponder *)firstField
{
    return startDateField;
}

- (void)loadFields
{
    [startDateField setStringValue:[[self model] startDate]];
    [endDateField setStringValue:[[self model] endDate]];
    [slotIndexSelector selectItemAtIndex:[[self model] slotIndex]];
    [slotNameField setStringValue:[[self model] slotName]];
}

- (void)saveFields
{
    [[self model] setSlotIndex:[slotIndexSelector indexOfSelectedItem]];
    [[self model] setSlotName:[slotNameField stringValue]];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    // We have to update start/end field in real time
    id control = [aNotification object];
    if (control == startDateField) {
        [[self model] setStartDate:[startDateField stringValue]];
    }
    else if (control == endDateField) {
        [[self model] setEndDate:[endDateField stringValue]];
    }
}
@end
