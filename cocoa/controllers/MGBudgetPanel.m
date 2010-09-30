/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBudgetPanel.h"
#import "MGDateFieldEditor.h"

@implementation MGBudgetPanel
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"BudgetPanel" pyClassName:@"PyBudgetPanel" parent:aParent];
    return self;
}

- (PyBudgetPanel *)py
{
    return (PyBudgetPanel *)py;
}

/* Override */
- (BOOL)isFieldDateField:(id)aField
{
    return (aField == startDateField) || (aField == stopDateField);
}

- (NSResponder *)firstField
{
    return startDateField;
}

- (void)loadFields
{
    [accountSelector removeAllItems];
    [accountSelector addItemsWithTitles:[[self py] accountOptions]];
    [targetSelector removeAllItems];
    [targetSelector addItemsWithTitles:[[self py] targetOptions]];
    [startDateField setStringValue:[[self py] startDate]];
    [stopDateField setStringValue:[[self py] stopDate]];
    [repeatEveryField setIntegerValue:[[self py] repeatEvery]];
    [accountSelector selectItemAtIndex:[[self py] accountIndex]];
    [targetSelector selectItemAtIndex:[[self py] targetIndex]];
    [amountField setStringValue:[[self py] amount]];
    [notesField setStringValue:[[self py] notes]];
}

- (void)saveFields
{
    [[self py] setStartDate:[startDateField stringValue]];
    [[self py] setStopDate:[stopDateField stringValue]];
    [[self py] setRepeatTypeIndex:[repeatOptionsPopUp indexOfSelectedItem]];
    [[self py] setRepeatEvery:[repeatEveryField intValue]];
    [[self py] setAccountIndex:[accountSelector indexOfSelectedItem]];
    [[self py] setTargetIndex:[targetSelector indexOfSelectedItem]];
    [[self py] setAmount:[amountField stringValue]];
    [[self py] setNotes:[notesField stringValue]];
}

/* Actions */
- (IBAction)repeatTypeSelected:(id)sender
{
    // The label next to the "every" field has to be updated as soon as the popup selection changes
    [[self py] setRepeatTypeIndex:[repeatOptionsPopUp indexOfSelectedItem]];
}

/* Python --> Cocoa */
- (void)refreshRepeatEvery
{
    [repeatEveryDescLabel setStringValue:[[self py] repeatEveryDesc]];
}

- (void)refreshRepeatOptions
{
    [repeatOptionsPopUp removeAllItems];
    NSArray *options = [[self py] repeatOptions];
    [repeatOptionsPopUp addItemsWithTitles:options];
    [repeatOptionsPopUp selectItemAtIndex:[[self py] repeatTypeIndex]];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    id control = [aNotification object];
    if (control == repeatEveryField) // must be edited right away to update the desc label
        [[self py] setRepeatEvery:[repeatEveryField intValue]];
    else if (control == startDateField) // must be edited right away to update the repeat options
        [[self py] setStartDate:[startDateField stringValue]];
}

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ((asker == startDateField) || (asker == stopDateField))
        return customDateFieldEditor;
    return nil;
}
@end