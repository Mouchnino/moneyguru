/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGMassEditionPanel.h"

@implementation MGMassEditionPanel
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"MassEditingPanel" pyClassName:@"PyMassEditionPanel" parent:aParent];
    currencies = [[[self py] availableCurrencies] retain];
    return self;
}

- (void)dealloc
{
    [currencies release];
    [super dealloc];
}

- (PyMassEditionPanel *)py
{
    return (PyMassEditionPanel *)py;
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

- (void)loadFields
{
    [currencySelector selectItemAtIndex:[[self py] currencyIndex]];
    // The rest all load through bindings
}

- (void)saveFields
{
    // all fields are saved through bindings.
}

/* Delegate */

- (id)comboBox:(NSComboBox *)aComboBox objectValueForItemAtIndex:(NSInteger)index
{
    if (index < 0)
    {
        return nil;
    }
    return [currencies objectAtIndex:index];
}

- (NSInteger)numberOfItemsInComboBox:(NSComboBox *)aComboBox
{
    return [currencies count];
}

- (NSUInteger)comboBox:(NSComboBox *)aComboBox indexOfItemWithStringValue:(NSString *)aString
{
    aString = [aString lowercaseString];
    for (int i=0; i<[currencies count]; i++)
    {
        NSString *s = [currencies objectAtIndex:i];
        if ([[s lowercaseString] isEqualTo:aString])
        {
            return i;
        }
    }
    return NSNotFound;
}

- (NSString *)comboBox:(NSComboBox *)aComboBox completedString:(NSString *)uncompletedString
{
    uncompletedString = [uncompletedString lowercaseString];
    for (int i=0; i<[currencies count]; i++)
    {
        NSString *s = [currencies objectAtIndex:i];
        if ([[s lowercaseString] hasPrefix:uncompletedString])
        {
            return s;
        }
    }
    return nil;
}

- (void)comboBoxSelectionDidChange:(NSNotification *)notification
{
    NSInteger currencyIndex = [currencySelector indexOfSelectedItem];
    [[self py] setCurrencyIndex:currencyIndex];
}

- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    // When the popup list is never popped (when only typing is used), this is what is called on tabbing out.
    NSInteger currencyIndex = [currencySelector indexOfSelectedItem];
    [[self py] setCurrencyIndex:currencyIndex];
}

/* Python --> Cocoa */
- (void)refresh
{
    // When we change the values in the py side, it doesn't work with KVO mechanism.
    // Notifications of a "py" change is enough to refresh all bound controls.
    [self willChangeValueForKey:@"py"];
    [self didChangeValueForKey:@"py"];
}
@end