#import "MGAccountReassignPanel.h"
#import "Utils.h"
#import "MGUtils.h"

@implementation MGAccountReassignPanel
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"AccountReassignPanel" pyClassName:@"PyAccountReassignPanel" pyParent:[aDocument py]];
    [self window]; // Initialize the window
    return self;
}

- (PyAccountReassignPanel *)py
{
    return (PyAccountReassignPanel *)py;
}

/* Public */
- (void)load
{
    [[self py] loadPanel];
    // Reload the account list
    [accountSelector removeAllItems];
    [accountSelector addItemsWithTitles:[[self py] availableAccounts]];
    [accountSelector selectItemAtIndex:[[self py] accountIndex]];
    [[self window] makeFirstResponder:accountSelector];
}

/* Actions */

- (IBAction)cancel:(id)sender
{
    [NSApp endSheet:[self window]];
}

- (IBAction)ok:(id)sender
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [[self py] setAccountIndex:[accountSelector indexOfSelectedItem]];
    [[self py] ok];
    [NSApp endSheet:[self window]];
}
@end
