/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTransactionInspector.h"
#import "Utils.h"
#import "MGFieldEditor.h"
#import "MGDateFieldEditor.h"
#import "MGUtils.h"

@implementation MGTransactionInspector
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"TransactionInspector" pyClassName:@"PyTransactionPanel" pyParent:[aDocument py]];
    [self window]; // Initialize the window
    customFieldEditor = [[MGFieldEditor alloc] init];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    [splitTable setTransactionPanel:[self py]];
    return self;
}

- (void)dealloc
{
    [customDateFieldEditor release];
    [customFieldEditor release];
    [super dealloc];
}

- (PyTransactionPanel *)py
{
    return (PyTransactionPanel *)py;
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
    return nil;
}

/* Python --> Cocoa */
- (void)refreshMCTButton
{
    [mctBalanceButton setEnabled:[[self py] canDoMCTBalance]];
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
    [descriptionField setStringValue:[[self py] description]];
    [payeeField setStringValue:[[self py] payee]];
    [checknoField setStringValue:[[self py] checkno]];
    [splitTable refresh];
    [[self window] makeFirstResponder:dateField];
}

- (void)save
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [[self py] setDescription:[descriptionField stringValue]];
    [[self py] setPayee:[payeeField stringValue]];
    [[self py] setCheckno:[checknoField stringValue]];
    [[self py] savePanel];
}

/* Actions */

- (IBAction)cancel:(id)sender
{
    [NSApp endSheet:[self window]];
}

- (IBAction)mctBalance:(id)sender
{
    [[self py] mctBalance];
}

- (IBAction)save:(id)sender
{
    [self save];
    [NSApp endSheet:[self window]];
}

/* Delegate */

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if (asker == dateField)
    {
        return customDateFieldEditor;
    }
    return customFieldEditor;
}

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
