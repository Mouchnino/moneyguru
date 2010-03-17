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
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"CustomDateRangePanel" pyClassName:@"PyCustomDateRangePanel" pyParent:[aDocument py]];
    [self window]; // Initialize the window
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    return self;
}

- (void)dealloc
{
    [customDateFieldEditor release];
    [super dealloc];
}

- (PyCustomDateRangePanel *)py
{
    return (PyCustomDateRangePanel *)py;
}

/* Public */
- (void)load
{
    [[self window] makeFirstResponder:nil];
    [[self py] loadPanel];
    [startDateField setStringValue:[[self py] startDate]];
    [endDateField setStringValue:[[self py] endDate]];
    [slotIndexSelector selectItemAtIndex:[[self py] slotIndex]];
    [slotNameField setStringValue:[[self py] slotName]];
    [[self window] makeFirstResponder:startDateField];
}

/* Actions */
- (IBAction)cancel:(id)sender
{
    [NSApp endSheet:[self window]];
}

- (IBAction)ok:(id)sender
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [[self py] setSlotIndex:[slotIndexSelector indexOfSelectedItem]];
    [[self py] setSlotName:[slotNameField stringValue]];
    [[self py] ok];
    [NSApp endSheet:[self window]];
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

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ((asker == startDateField) || (asker == endDateField)) {
        return customDateFieldEditor;
    }
    return nil;
}

@end
