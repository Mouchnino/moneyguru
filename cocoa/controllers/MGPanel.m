/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGPanel.h"
#import "MGTextField.h"

@implementation MGPanel
- (PyPanel *)py
{
    return (PyPanel *)py;
}

/* Virtual */
- (NSString *)fieldOfTextField:(NSTextField *)textField
{
    // if textField is a field to perform auto-complete on, return the name of the field for auto-completion
    return nil;
}

- (NSResponder *)firstField
{
    // The first field to get focus after a load
    return nil;
}

- (void)loadFields
{
}

- (void)saveFields
{
}

/* Public */
- (BOOL)canLoad
{
    return [[self py] canLoadPanel];
}

- (void)load
{
    // Is the date field is already the first responder, the date being set will not correctly go down
    // the py widget during makeFirstResponder:
    [[self window] makeFirstResponder:nil];
    [[self py] loadPanel];
    // When we change the values in the py side, it doesn't work with KVO mechanism.
    // Notifications of a "py" change is enough to refresh all bound controls.
    [self willChangeValueForKey:@"py"];
    [self didChangeValueForKey:@"py"];
    [self loadFields];
    [[self window] makeFirstResponder:[self firstField]];
}

- (void)save
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [self saveFields];
    [[self py] savePanel];
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
@end