/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGCustomDateRangePanel.h"
#import "Utils.h"
#import "MGDateFieldEditor.h"

@implementation MGCustomDateRangePanel
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"CustomDateRangePanel" pyClassName:@"PyCustomDateRangePanel" parent:aParent];
    return self;
}

- (PyCustomDateRangePanel *)py
{
    return (PyCustomDateRangePanel *)py;
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
    [startDateField setStringValue:[[self py] startDate]];
    [endDateField setStringValue:[[self py] endDate]];
    [slotIndexSelector selectItemAtIndex:[[self py] slotIndex]];
    [slotNameField setStringValue:[[self py] slotName]];
}

- (void)saveFields
{
    [[self py] setSlotIndex:[slotIndexSelector indexOfSelectedItem]];
    [[self py] setSlotName:[slotNameField stringValue]];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    // We have to update start/end field in real time
    id control = [aNotification object];
    if (control == startDateField) {
        [[self py] setStartDate:[startDateField stringValue]];
    }
    else if (control == endDateField) {
        [[self py] setEndDate:[endDateField stringValue]];
    }
}
@end
