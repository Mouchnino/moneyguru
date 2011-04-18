/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGAccountReassignPanel.h"
#import "Utils.h"

@implementation MGAccountReassignPanel
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"AccountReassignPanel" pyClassName:@"PyAccountReassignPanel" parent:aParent];
    return self;
}

- (PyAccountReassignPanel *)py
{
    return (PyAccountReassignPanel *)py;
}

/* Override */
- (NSResponder *)firstField
{
    return accountSelector;
}

- (void)loadFields
{
    [accountSelector removeAllItems];
    [accountSelector addItemsWithTitles:[[self py] availableAccounts]];
    [accountSelector selectItemAtIndex:[[self py] accountIndex]];
}

- (void)saveFields
{
    [[self py] setAccountIndex:[accountSelector indexOfSelectedItem]];
}
@end
