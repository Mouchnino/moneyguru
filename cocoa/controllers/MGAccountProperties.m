/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGAccountProperties.h"
#import "MGConst.h"

@implementation MGAccountProperties
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"AccountProperties" pyClassName:@"PyAccountPanel" parent:aParent];
    currencies = [[[self py] availableCurrencies] retain];
    /* If we don't reload data, we'll have a 0-length combobox at loadFields */
    [currencySelector reloadData];
    return self;
}

- (void)dealloc
{
    [currencies release];
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
    [typeSelector selectItemAtIndex:[[self py] typeIndex]];
    [currencySelector selectItemAtIndex:[[self py] currencyIndex]];
    [accountNumberTextField setStringValue:[[self py] accountNumber]];
}

- (void)saveFields
{
    [[self py] setName:[nameTextField stringValue]];
    NSInteger currencyIndex = [currencySelector indexOfSelectedItem];
    if (currencyIndex >= 0)
        [[self py] setCurrencyIndex:currencyIndex];
    [[self py] setTypeIndex:[typeSelector indexOfSelectedItem]];
    [[self py] setAccountNumber:[accountNumberTextField stringValue]];
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
@end