#import "MGMassEditionPanel.h"
#import "MGDateFieldEditor.h"
#import "MGUtils.h"

@implementation MGMassEditionPanel
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"MassEditionPanel" pyClassName:@"PyMassEditionPanel" pyParent:[aDocument py]];
    currencies = [[[self py] availableCurrencies] retain];
    customFieldEditor = [[MGFieldEditor alloc] init];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    return self;
}

- (void)dealloc
{
    [customDateFieldEditor release];
    [customFieldEditor release];
    [currencies release];
    [super dealloc];
}

- (PyMassEditionPanel *)py
{
    return (PyMassEditionPanel *)py;
}

/* Private */

- (NSString *)fieldOfTextField:(NSTextField *)textField
{
    if (textField == dateField)
    {
        return @"date";
    }
    else if (textField == descriptionField)
    {
        return @"description";
    }
    else if (textField == payeeField)
    {
        return @"payee";
    }
    else if (textField == checknoField)
    {
        return @"checkno";
    }
    else if (textField == fromField)
    {
        return @"from";
    }
    else if (textField == toField)
    {
        return @"to";
    }
    return nil;
}

/* NSWindow delegate */

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if (asker == dateField)
    {
        return customDateFieldEditor;
    }
    return customFieldEditor;
}

/* MGTextField Delegate */

- (NSString *)autoCompletionForTextField:(MGTextField *)textField partialWord:(NSString *)text
{
    NSString *attr = [self fieldOfTextField:textField];
    if (attr != nil)
    {
        return [[self py] completeValue:text forAttribute:attr];
    }
    return nil;
}

- (NSString *)currentValueForTextField:(MGTextField *)textField
{
    return [[self py] currentCompletion];
}

- (NSString *)prevValueForTextField:(MGTextField *)textField
{
    return [[self py] prevCompletion];
}

- (NSString *)nextValueForTextField:(MGTextField *)textField
{
    return [[self py] nextCompletion];
}

/* Public */

- (BOOL)canLoad
{
    return [[self py] canLoadPanel];
}

- (void)load
{
    [[self py] loadPanel];
    [self refresh];
    [currencySelector selectItemAtIndex:[[self py] currencyIndex]];
    [[self window] makeFirstResponder:dateField];
}

- (void)save
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [[self py] savePanel];
}

- (void)refresh
{
    // When we change the values in the py side, it doesn't work with KVO mechanism.
    // Notifications of a "py" change is enough to refresh all bound controls.
    [self willChangeValueForKey:@"py"];
    [self didChangeValueForKey:@"py"];
}

/* Actions */

- (IBAction)cancel:(id)sender
{
    [NSApp endSheet:[self window]];
}

- (IBAction)save:(id)sender
{
    [self save];
    [NSApp endSheet:[self window]];
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

- (void)comboBoxSelectionDidChange:(NSNotification *)notification
{
    int currencyIndex = [currencySelector indexOfSelectedItem];
    [[self py] setCurrencyIndex:currencyIndex];
}

- (void)controlTextDidEndEditing:(NSNotification *)aNotification
{
    // When the popup list is never popped (when only typing is used), this is what is called on tabbing out.
    int currencyIndex = [currencySelector indexOfSelectedItem];
    [[self py] setCurrencyIndex:currencyIndex];
}
@end