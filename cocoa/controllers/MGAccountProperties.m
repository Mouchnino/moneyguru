/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountProperties.h"
#import "MGConst.h"
#import "MGMainWindowController.h"
#import "Utils.h"

@implementation MGAccountProperties
- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyAccountPanel *m = [[PyAccountPanel alloc] initWithModel:[[aParent model] accountPanel]];
    self = [super initWithNibName:@"AccountPanel" model:m parent:aParent];
    [m bindCallback:createCallback(@"PanelView", self)];
    [m release];
    [self window];
    typePopUp = [[HSPopUpList2 alloc] initWithPyRef:[[self model] typeList] popupView:typeSelector];
    currencyComboBox = [[HSComboBox2 alloc] initWithPyRef:[[self model] currencyList] view:currencySelector];
    return self;
}

- (void)dealloc
{
    [typePopUp release];
    [currencyComboBox release];
    [super dealloc];
}

- (PyAccountPanel *)model
{
    return (PyAccountPanel *)model;
}

/* Override */
- (NSResponder *)firstField
{
    return nameTextField;
}

- (void)loadFields
{
    [nameTextField setStringValue:[[self model] name]];
    [accountNumberTextField setStringValue:[[self model] accountNumber]];
    [notesTextField setStringValue:[[self model] notes]];
    [currencySelector setEnabled:[[self model] canChangeCurrency]];
}

- (void)saveFields
{
    [[self model] setName:[nameTextField stringValue]];
    [[self model] setAccountNumber:[accountNumberTextField stringValue]];
    [[self model] setNotes:[notesTextField stringValue]];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"AccountPanel";
}
@end