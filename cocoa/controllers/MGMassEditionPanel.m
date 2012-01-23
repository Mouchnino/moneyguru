/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGMassEditionPanel.h"
#import "MGMainWindowController.h"
#import "Utils.h"

@implementation MGMassEditionPanel
- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyMassEditionPanel *m = [[PyMassEditionPanel alloc] initWithModel:[[aParent model] massEditPanel]];
    self = [super initWithNibName:@"MassEditingPanel" model:m parent:aParent];
    [m bindCallback:createCallback(@"PanelView", self)];
    [m release];
    [self window];
    currencyComboBox = [[HSComboBox alloc] initWithPyRef:[[self model] currencyList] view:currencySelector];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)dealloc
{
    [currencyComboBox release];
    [super dealloc];
}

- (PyMassEditionPanel *)model
{
    return (PyMassEditionPanel *)model;
}

/* Override */
- (NSString *)completionAttrForField:(id)aField
{
    if (aField == descriptionField) {
        return @"description";
    }
    else if (aField == payeeField) {
        return @"payee";
    }
    else if (aField == fromField) {
        return @"from";
    }
    else if (aField == toField) {
        return @"to";
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

- (void)loadCheckboxes
{
    [dateCheckBox setState:[[self model] dateEnabled] ? NSOnState : NSOffState];
    [descriptionCheckBox setState:[[self model] descriptionEnabled] ? NSOnState : NSOffState];
    [payeeCheckBox setState:[[self model] payeeEnabled] ? NSOnState : NSOffState];
    [checknoCheckBox setState:[[self model] checknoEnabled] ? NSOnState : NSOffState];
    [fromCheckBox setState:[[self model] fromEnabled] ? NSOnState : NSOffState];
    [toCheckBox setState:[[self model] toEnabled] ? NSOnState : NSOffState];
    [amountCheckBox setState:[[self model] amountEnabled] ? NSOnState : NSOffState];
    [currencyCheckBox setState:[[self model] currencyEnabled] ? NSOnState : NSOffState];
}

- (void)loadFields
{
    [self loadCheckboxes];
    [dateField setStringValue:[[self model] date]];
    [descriptionField setStringValue:[[self model] description]];
    [payeeField setStringValue:[[self model] payee]];
    [checknoField setStringValue:[[self model] checkno]];
    [fromField setStringValue:[[self model] fromAccount]];
    [toField setStringValue:[[self model] to]];
    [amountField setStringValue:[[self model] amount]];
    [fromCheckBox setEnabled:[[self model] canChangeAccounts]];
    [toCheckBox setEnabled:[[self model] canChangeAccounts]];
    [amountCheckBox setEnabled:[[self model] canChangeAmount]];
    [fromField setEnabled:[[self model] canChangeAccounts]];
    [toField setEnabled:[[self model] canChangeAccounts]];
    [amountField setEnabled:[[self model] canChangeAmount]];
}

- (void)saveFields
{
    [[self model] setDateEnabled:[dateCheckBox state] == NSOnState];
    [[self model] setDescriptionEnabled:[descriptionCheckBox state] == NSOnState];
    [[self model] setPayeeEnabled:[payeeCheckBox state] == NSOnState];
    [[self model] setChecknoEnabled:[checknoCheckBox state] == NSOnState];
    [[self model] setFromEnabled:[fromCheckBox state] == NSOnState];
    [[self model] setToEnabled:[toCheckBox state] == NSOnState];
    [[self model] setAmountEnabled:[amountCheckBox state] == NSOnState];
    [[self model] setCurrencyEnabled:[currencyCheckBox state] == NSOnState];
}

/* Delegate */
- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    id control = [aNotification object];
    /* XXX This is all really ugly, but this panel used to use KVO bindings which don't work with
       ObjP. I'm too busy to fix this cleanly now, but I'll get to it eventually.
    */
    if (control == dateField) {
        [[self model] setDate:[dateField stringValue]];
    }
    else if (control == descriptionField) {
        [[self model] setDescription:[descriptionField stringValue]];
    }
    else if (control == payeeField) {
        [[self model] setPayee:[payeeField stringValue]];
    }
    else if (control == checknoField) {
        [[self model] setCheckno:[checknoField stringValue]];
    }
    else if (control == fromField) {
        [[self model] setFromAccount:[fromField stringValue]];
    }
    else if (control == toField) {
        [[self model] setTo:[toField stringValue]];
    }
    else if (control == amountField) {
        [[self model] setAmount:[amountField stringValue]];
    }
}

/* Model --> View */
- (void)refresh
{
    [self loadCheckboxes];
}
@end