/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGTransactionInspector.h"
#import "Utils.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"
#import "NSEventAdditions.h"
#import "MGMainWindowController.h"

@implementation MGTransactionInspector
- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyTransactionPanel *m = [[PyTransactionPanel alloc] initWithModel:[[aParent model] transactionPanel]];
    self = [super initWithNibName:@"TransactionPanel" model:m parent:aParent];
    [m bindCallback:createCallback(@"PanelWithTransactionView", self)];
    [m release];
    splitTable = [[MGSplitTable alloc] initWithPyRef:[[self model] splitTable] tableView:splitTableView];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)dealloc
{
    [splitTable release];
    [super dealloc];
}

- (PyTransactionPanel *)model
{
    return (PyTransactionPanel *)model;
}

/* MGPanel Overrides */
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
    return aField == dateField;
}

- (NSResponder *)firstField
{
    return dateField;
}

- (void)loadFields
{
    [tabView selectFirstTabViewItem:self];
    [dateField setStringValue:[[self model] date]];
    [descriptionField setStringValue:[[self model] description]];
    [payeeField setStringValue:[[self model] payee]];
    [checknoField setStringValue:[[self model] checkno]];
    [notesField setStringValue:[[self model] notes]];
    [splitTable refresh];
}

- (void)saveFields
{
    [[self model] setDate:[dateField stringValue]];
    [[self model] setDescription:[descriptionField stringValue]];
    [[self model] setPayee:[payeeField stringValue]];
    [[self model] setCheckno:[checknoField stringValue]];
    [[self model] setNotes:[notesField stringValue]];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"TransactionPanel";
}

/* Python --> Cocoa */
- (void)refreshForMultiCurrency
{
    [mctBalanceButton setEnabled:[[self model] isMultiCurrency]];
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

- (IBAction)mctBalance:(id)sender
{
    [[self model] mctBalance];
}
@end
