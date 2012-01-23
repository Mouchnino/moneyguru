/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSchedulePanel.h"
#import "MGMainWindowController.h"
#import "Utils.h"

@implementation MGSchedulePanel
- (id)initWithParent:(MGMainWindowController *)aParent
{
    PySchedulePanel *m = [[PySchedulePanel alloc] initWithModel:[[aParent model] schedulePanel]];
    self = [super initWithNibName:@"SchedulePanel" model:m parent:aParent];
    [m bindCallback:createCallback(@"SchedulePanelView", self)];
    [m release];
    splitTable = [[MGSplitTable alloc] initWithPyRef:[[self model] splitTable] tableView:splitTableView];
    repeatTypePopUp = [[HSPopUpList alloc] initWithPyRef:[[self model] repeatTypeList] popupView:repeatTypePopUpView];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)dealloc
{
    [repeatTypePopUp release];
    [splitTable release];
    [super dealloc];
}

- (PySchedulePanel *)model
{
    return (PySchedulePanel *)model;
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
    [startDateField setStringValue:[[self model] startDate]];
    [stopDateField setStringValue:[[self model] stopDate]];
    [repeatEveryField setIntegerValue:[[self model] repeatEvery]];
    [descriptionField setStringValue:[[self model] description]];
    [payeeField setStringValue:[[self model] payee]];
    [checknoField setStringValue:[[self model] checkno]];
    [notesField setStringValue:[[self model] notes]];
    [splitTable refresh];
}

- (void)saveFields
{
    [[self model] setStartDate:[startDateField stringValue]];
    [[self model] setStopDate:[stopDateField stringValue]];
    [[self model] setRepeatEvery:[repeatEveryField intValue]];
    [[self model] setDescription:[descriptionField stringValue]];
    [[self model] setPayee:[payeeField stringValue]];
    [[self model] setCheckno:[checknoField stringValue]];
    [[self model] setNotes:[notesField stringValue]];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"SchedulePanel";
}

/* Actions */
- (IBAction)addSplit:(id)sender
{
    [[splitTable model] add];
}

- (IBAction)deleteSplit:(id)sender
{
    [[splitTable model] deleteSelectedRows];
}

/* Python --> Cocoa */
- (void)refreshForMultiCurrency
{
}

- (void)refreshRepeatEvery
{
    [repeatEveryDescLabel setStringValue:[[self model] repeatEveryDesc]];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    id control = [aNotification object];
    if (control == repeatEveryField) {
        // must be edited right away to update the desc label
        [[self model] setRepeatEvery:[repeatEveryField intValue]];
    }
    else if (control == startDateField) {
        // must be edited right away to update the repeat options
        [[self model] setStartDate:[startDateField stringValue]];
    }
    // for the repeatType field, it's handled in repeatTypeSelected:
}
@end
