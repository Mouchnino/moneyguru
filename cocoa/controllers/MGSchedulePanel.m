/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSchedulePanel.h"
#import "Utils.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"
#import "MGUtils.h"

@implementation MGSchedulePanel
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"SchedulePanel" pyClassName:@"PySchedulePanel" pyParent:[aDocument py]];
    [self window]; // Initialize the window
    customFieldEditor = [[MGFieldEditor alloc] init];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    [splitTable setTransactionPanel:[self py]];
    return self;
}

- (void)dealloc
{
    [customDateFieldEditor release];
    [customFieldEditor release];
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
    [startDateField setStringValue:[[self py] startDate]];
    [stopDateField setStringValue:[[self py] stopDate]];
    [repeatOptionsPopUp selectItemAtIndex:[[self py] repeatTypeIndex]];
    [repeatEveryField setIntValue:[[self py] repeatEvery]];
    [descriptionField setStringValue:[[self py] description]];
    [payeeField setStringValue:[[self py] payee]];
    [checknoField setStringValue:[[self py] checkno]];
    [splitTable refresh];
    [self refreshRepeatOptions];
}

- (void)saveFields
{
    [[self py] setStartDate:[startDateField stringValue]];
    [[self py] setStopDate:[stopDateField stringValue]];
    [[self py] setRepeatTypeIndex:[repeatOptionsPopUp indexOfSelectedItem]];
    [[self py] setDescription:[descriptionField stringValue]];
    [[self py] setPayee:[payeeField stringValue]];
    [[self py] setCheckno:[checknoField stringValue]];
}

/* Public */
- (void)new
{
    [[self window] makeFirstResponder:nil];
    [[self py] newItem];
    [self loadFields];
    [[self window] makeFirstResponder:startDateField];
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
    int index = [repeatOptionsPopUp indexOfSelectedItem];
    [repeatOptionsPopUp removeAllItems];
    NSArray *options = [[self py] repeatOptions];
    [repeatOptionsPopUp addItemsWithTitles:options];
    [repeatOptionsPopUp selectItemAtIndex:index];
}

/* Delegate */

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ((asker == startDateField) || (asker == stopDateField))
    {
        return customDateFieldEditor;
    }
    return customFieldEditor;
}
@end
