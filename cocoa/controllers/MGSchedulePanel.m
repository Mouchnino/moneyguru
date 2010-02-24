/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSchedulePanel.h"
#import "Utils.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"

@implementation MGSchedulePanel
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"SchedulePanel" pyClassName:@"PySchedulePanel" document:aDocument];
    [self window]; // Initialize the window
    customFieldEditor = [[MGFieldEditor alloc] init];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    splitTable = [[MGSplitTable alloc] initWithTransactionPanel:[self py] view:splitTableView];
    [splitTable connect];
    return self;
}

- (void)dealloc
{
    [customDateFieldEditor release];
    [customFieldEditor release];
    [splitTable release];
    [super dealloc];
}

- (PySchedulePanel *)py
{
    return (PySchedulePanel *)py;
}

/* Override */
- (NSString *)fieldOfTextField:(NSTextField *)textField
{
    if (textField == descriptionField)
    {
        return @"description";
    }
    else if (textField == payeeField)
    {
        return @"payee";
    }
    return nil;
}

- (NSResponder *)firstField
{
    return startDateField;
}

- (void)loadFields
{
    [tabView selectFirstTabViewItem:self];
    [startDateField setStringValue:[[self py] startDate]];
    [stopDateField setStringValue:[[self py] stopDate]];
    [repeatOptionsPopUp selectItemAtIndex:[[self py] repeatTypeIndex]];
    [repeatEveryField setIntegerValue:[[self py] repeatEvery]];
    [descriptionField setStringValue:[[self py] description]];
    [payeeField setStringValue:[[self py] payee]];
    [checknoField setStringValue:[[self py] checkno]];
    [notesField setStringValue:[[self py] notes]];
    [amountField setStringValue:[[self py] amount]];
    [amountField2 setStringValue:[[self py] amount]];
    [splitTable refresh];
}

- (void)saveFields
{
    [[self py] setStartDate:[startDateField stringValue]];
    [[self py] setStopDate:[stopDateField stringValue]];
    [[self py] setRepeatTypeIndex:[repeatOptionsPopUp indexOfSelectedItem]];
    [[self py] setRepeatEvery:[repeatEveryField intValue]];
    [[self py] setDescription:[descriptionField stringValue]];
    [[self py] setPayee:[payeeField stringValue]];
    [[self py] setCheckno:[checknoField stringValue]];
    [[self py] setNotes:[notesField stringValue]];
    [[self py] setAmount:[amountField stringValue]];
}

/* Actions */
- (IBAction)addSplit:(id)sender
{
    [[splitTable py] add];
}

- (IBAction)deleteSplit:(id)sender
{
    [[splitTable py] deleteSelectedRows];
}

- (IBAction)repeatTypeSelected:(id)sender
{
    // The label next to the "every" field has to be updated as soon as the popup selection changes
    [[self py] setRepeatTypeIndex:[repeatOptionsPopUp indexOfSelectedItem]];
}

/* Python --> Cocoa */
- (void)refreshAmount
{
    [amountField setStringValue:[[self py] amount]];
    [amountField2 setStringValue:[[self py] amount]];
}

- (void)refreshForMultiCurrency
{
    BOOL mct = [[self py] isMultiCurrency];
    [amountField setEnabled:!mct];
    [amountField2 setEnabled:!mct];
    [mctNotice setHidden:!mct];
    [mctNotice2 setHidden:!mct];
}

- (void)refreshRepeatEvery
{
    [repeatEveryDescLabel setStringValue:[[self py] repeatEveryDesc]];
}

- (void)refreshRepeatOptions
{
    NSInteger index = [repeatOptionsPopUp indexOfSelectedItem];
    [repeatOptionsPopUp removeAllItems];
    NSArray *options = [[self py] repeatOptions];
    [repeatOptionsPopUp addItemsWithTitles:options];
    [repeatOptionsPopUp selectItemAtIndex:index];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    id control = [aNotification object];
    if (control == repeatEveryField) {
        // must be edited right away to update the desc label
        [[self py] setRepeatEvery:[repeatEveryField intValue]];
    }
    else if (control == startDateField) {
        // must be edited right away to update the repeat options
        [[self py] setStartDate:[startDateField stringValue]];
    }
    else if ((control == amountField) || (control == amountField2)) {
        // must be edited right away to refresh the split table
        [[self py] setAmount:[(NSTextField *)control stringValue]];
    }
    // for the repeatType field, it's handled in repeatTypeSelected:
}

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ((asker == startDateField) || (asker == stopDateField))
    {
        return customDateFieldEditor;
    }
    return customFieldEditor;
}
@end
