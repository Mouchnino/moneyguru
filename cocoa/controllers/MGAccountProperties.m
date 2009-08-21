/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGAccountProperties.h"
#import "MGConst.h"
#import "MGUtils.h"

@implementation MGAccountProperties
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"AccountProperties" pyClassName:@"PyAccountPanel" document:aDocument];
    // We have to initialize the currencies before the widgets if we want the inital data source call
    // to return something
    currencies = [[[self py] availableCurrencies] retain];
    [self window]; // Initialize the window
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
    // Reload the budget target list
    [budgetTargetSelector removeAllItems];
    [budgetTargetSelector addItemsWithTitles:[[self py] availableBudgetTargets]];
    // When we change the values in the py side, it doesn't work with KVO mechanism.
    // Notifications of a "py" change is enough to refresh all bound controls.
    [self willChangeValueForKey:@"py"];
    [self didChangeValueForKey:@"py"];
    [self willChangeValueForKey:@"typeIndex"];
    [self didChangeValueForKey:@"typeIndex"];
    [nameTextField setStringValue:[[self py] name]];
    [currencySelector selectItemAtIndex:[[self py] currencyIndex]];
    [budgetTargetSelector selectItemAtIndex:[[self py] budgetTargetIndex]];
}

- (void)saveFields
{
    [[self py] setName:[nameTextField stringValue]];
    int currencyIndex = [currencySelector indexOfSelectedItem];
    if (currencyIndex >= 0)
    {
        [[self py] setCurrencyIndex:currencyIndex];
    }
    int budgetTargetIndex = [budgetTargetSelector indexOfSelectedItem];
    if (budgetTargetIndex >= 0)
    {
        [[self py] setBudgetTargetIndex:budgetTargetIndex];
    }
}

/* Properties */
- (int)typeIndex
{
    return [[self py] typeIndex];
}

- (void)setTypeIndex:(int)typeIndex
{
    [self willChangeValueForKey:@"py"];
    [[self py] setTypeIndex:typeIndex];
    [self didChangeValueForKey:@"py"];
}

/* Delegate */

- (id)comboBox:(NSComboBox *)aComboBox objectValueForItemAtIndex:(int)index
{
    if (index < 0)
    {
        return nil;
    }
    return [currencies objectAtIndex:index];
}

- (int)numberOfItemsInComboBox:(NSComboBox *)aComboBox
{
    return [currencies count];
}

- (int)comboBox:(NSComboBox *)aComboBox indexOfItemWithStringValue:(NSString *)aString
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

- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    // This is so the budget field is updated as soon as the field is left
    [self willChangeValueForKey:@"py"];
    [self didChangeValueForKey:@"py"];
}

@end