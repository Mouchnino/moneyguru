/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

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
    self = [super initWithNibName:@"TransactionInspector" pyClassName:@"PyTransactionPanel" document:aDocument];
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

/* Override */
- (NSString *)fieldOfTextField:(NSTextField *)textField
{
    if (textField == descriptionField)
    {
        return @"description";
    }
    else if (textField == payeeField)
    {
        return @"payee";
    }
    return nil;
}

- (NSResponder *)firstField
{
    return dateField;
}

- (void)loadFields
{
    [descriptionField setStringValue:[[self py] description]];
    [payeeField setStringValue:[[self py] payee]];
    [checknoField setStringValue:[[self py] checkno]];
    [splitTable refresh];
}

- (void)saveFields
{
    [[self py] setDescription:[descriptionField stringValue]];
    [[self py] setPayee:[payeeField stringValue]];
    [[self py] setCheckno:[checknoField stringValue]];
}

/* Python --> Cocoa */
- (void)refreshMCTButton
{
    [mctBalanceButton setEnabled:[[self py] canDoMCTBalance]];
}

/* Actions */
- (IBAction)mctBalance:(id)sender
{
    [[self py] mctBalance];
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
@end
