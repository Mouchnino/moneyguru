/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountProperties.h"
#import "MGConst.h"

@implementation MGAccountProperties
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"AccountPanel" pyClassName:@"PyAccountPanel" parent:aParent];
    [self window];
    typePopUp = [[HSPopUpList alloc] initWithPy:[[self py] typeList] view:typeSelector];
    currencyComboBox = [[HSComboBox alloc] initWithPy:[[self py] currencyList] view:currencySelector];
    return self;
}

- (void)dealloc
{
    [typePopUp release];
    [currencyComboBox release];
    [super dealloc];
}

- (PyAccountPanel *)py
{
    return (PyAccountPanel *)py;
}

/* Override */
- (NSResponder *)firstField
{
    return nameTextField;
}

- (void)loadFields
{
    [nameTextField setStringValue:[[self py] name]];
    [accountNumberTextField setStringValue:[[self py] accountNumber]];
    [notesTextField setStringValue:[[self py] notes]];
    [currencySelector setEnabled:[[self py] canChangeCurrency]];
}

- (void)saveFields
{
    [[self py] setName:[nameTextField stringValue]];
    [[self py] setAccountNumber:[accountNumberTextField stringValue]];
    [[self py] setNotes:[notesTextField stringValue]];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"AccountPanel";
}
@end