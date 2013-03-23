/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGMassEditionPanel.h"
#import "MGMassEditionPanel_UI.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

@implementation MGMassEditionPanel

@synthesize dateFieldView;
@synthesize descriptionFieldView;
@synthesize payeeFieldView;
@synthesize checknoFieldView;
@synthesize fromFieldView;
@synthesize toFieldView;
@synthesize amountFieldView;
@synthesize currencyComboBoxView;
@synthesize dateCheckBox;
@synthesize descriptionCheckBox;
@synthesize payeeCheckBox;
@synthesize checknoCheckBox;
@synthesize fromCheckBox;
@synthesize toCheckBox;
@synthesize amountCheckBox;
@synthesize currencyCheckBox;

- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyMassEditionPanel *m = [[PyMassEditionPanel alloc] initWithModel:[[aParent model] massEditPanel]];
    self = [super initWithModel:m parent:aParent];
    [m bindCallback:createCallback(@"PanelView", self)];
    [m release];
    [self setWindow:createMGMassEditionPanel_UI(self)];
    dateField = [[HSTextField alloc] initWithPyRef:[[self model] dateField] view:dateFieldView];
    descriptionField = [[HSTextField alloc] initWithPyRef:[[self model] descriptionField] view:descriptionFieldView];
    payeeField = [[HSTextField alloc] initWithPyRef:[[self model] payeeField] view:payeeFieldView];
    checknoField = [[HSTextField alloc] initWithPyRef:[[self model] checknoField] view:checknoFieldView];
    fromField = [[HSTextField alloc] initWithPyRef:[[self model] fromField] view:fromFieldView];
    toField = [[HSTextField alloc] initWithPyRef:[[self model] toField] view:toFieldView];
    amountField = [[HSTextField alloc] initWithPyRef:[[self model] amountField] view:amountFieldView];
    currencyComboBoxView.completes = YES;
    currencyComboBox = [[HSComboBox alloc] initWithPyRef:[[self model] currencyList] view:currencyComboBoxView];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyRef:[[self model] completableEdit]];
    return self;
}

- (void)dealloc
{
    [dateField release];
    [descriptionField release];
    [payeeField release];
    [checknoField release];
    [fromField release];
    [toField release];
    [amountField release];
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
    if (aField == descriptionFieldView) {
        return @"description";
    }
    else if (aField == payeeFieldView) {
        return @"payee";
    }
    else if (aField == fromFieldView) {
        return @"from";
    }
    else if (aField == toFieldView) {
        return @"to";
    }
    return nil;
}

- (BOOL)isFieldDateField:(id)aField
{
    return aField == dateFieldView;
}

- (NSResponder *)firstField
{
    return dateFieldView;
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
    [fromCheckBox setEnabled:[[self model] canChangeAccounts]];
    [toCheckBox setEnabled:[[self model] canChangeAccounts]];
    [amountCheckBox setEnabled:[[self model] canChangeAmount]];
    [fromFieldView setEnabled:[[self model] canChangeAccounts]];
    [toFieldView setEnabled:[[self model] canChangeAccounts]];
    [amountFieldView setEnabled:[[self model] canChangeAmount]];
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

/* Model --> View */
- (void)refresh
{
    [self loadCheckboxes];
}
@end