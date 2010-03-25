/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSchedulePanel.h"
#import "Utils.h"

@implementation MGSchedulePanel
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"SchedulePanel" pyClassName:@"PySchedulePanel" parent:aParent];
    splitTable = [[MGSplitTable alloc] initWithTransactionPanel:[self py] view:splitTableView];
    [splitTable connect];
    return self;
}

- (void)dealloc
{
    [splitTable release];
    [super dealloc];
}

- (PySchedulePanel *)py
{
    return (PySchedulePanel *)py;
}

/* MGPanel Override */
- (NSString *)completionAttrForField:(id)aField
{
    if (aField == descriptionField) {
        return @"description";
    }
    else if (aField == payeeField) {
        return @"payee";
    }
    else if (aField == splitTableView) {
        NSString *name = [splitTable editedFieldname];
        if ((name != nil) && ([name isEqualTo:@"account"])) {
            return @"account";
        }
    }
    return nil;
}

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
    [tabView selectFirstTabViewItem:self];
    [startDateField setStringValue:[[self py] startDate]];
    [stopDateField setStringValue:[[self py] stopDate]];
    [repeatOptionsPopUp selectItemAtIndex:[[self py] repeatTypeIndex]];
    [repeatEveryField setIntegerValue:[[self py] repeatEvery]];
    [descriptionField setStringValue:[[self py] description]];
    [payeeField setStringValue:[[self py] payee]];
    [checknoField setStringValue:[[self py] checkno]];
    [notesField setStringValue:[[self py] notes]];
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
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"SchedulePanel";
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
- (void)refreshForMultiCurrency
{
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
    // for the repeatType field, it's handled in repeatTypeSelected:
}
@end
