/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

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
    repeatTypePopUp = [[HSPopUpList alloc] initWithPy:[[self py] repeatTypeList] view:repeatTypePopUpView];
    accountPopUp = [[HSPopUpList alloc] initWithPy:[[self py] accountList] view:accountSelector];
    targetPopUp = [[HSPopUpList alloc] initWithPy:[[self py] targetList] view:targetSelector];
    return self;
}

- (void)dealloc
{
    [repeatTypePopUp release];
    [super dealloc];
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
    [startDateField setStringValue:[[self py] startDate]];
    [stopDateField setStringValue:[[self py] stopDate]];
    [repeatEveryField setIntegerValue:[[self py] repeatEvery]];
    [amountField setStringValue:[[self py] amount]];
    [notesField setStringValue:[[self py] notes]];
}

- (void)saveFields
{
    [[self py] setStartDate:[startDateField stringValue]];
    [[self py] setStopDate:[stopDateField stringValue]];
    [[self py] setRepeatEvery:[repeatEveryField intValue]];
    [[self py] setAmount:[amountField stringValue]];
    [[self py] setNotes:[notesField stringValue]];
}

/* Python --> Cocoa */
- (void)refreshRepeatEvery
{
    [repeatEveryDescLabel setStringValue:[[self py] repeatEveryDesc]];
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