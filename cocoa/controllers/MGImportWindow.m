/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGImportWindow.h"
#import "PSMTabBarCell.h"

@implementation MGImportWindow
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyImportWindow" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"ImportWindow" owner:self];
    [tabBar setSizeCellsToFit:YES];
    [tabBar setCanCloseOnlyTab:YES];
    importTable = [[MGImportTable alloc] initWithPy:[[self py] importTable] view:importTableView];
    return self;
}

- (void)dealloc
{
    [importTable release];
    [super dealloc];
}

- (PyImportWindow *)py
{
    return (PyImportWindow *)py;
}

/* Actions */
- (IBAction)changeTargetAccount:(id)sender
{
    [[self py] setSelectedTargetAccountIndex:[targetAccountsPopup indexOfSelectedItem]];
    [importTable updateOneOrTwoSided];
}

- (IBAction)importSelectedPane:(id)sender
{
    [[self py] importSelectedPane];
}

- (IBAction)selectSwapType:(id)sender
{
    [[self py] setSwapTypeIndex:[switchDateFieldsPopup indexOfSelectedItem]];
    [swapButton setEnabled:[[self py] canPerformSwap]];
}

- (IBAction)switchDateFields:(id)sender
{
    BOOL applyToAll = [applySwapToAllCheckbox state] == NSOnState;
    if ([[self py] canPerformSwap]) {
        [[self py] performSwap:applyToAll];
    }
}

/* Delegate */

// We use "willClose" because it's not possible to know the aTabViewItem's index after the fact
- (void)tabView:(NSTabView *)aTabView willCloseTabViewItem:(NSTabViewItem *)aTabViewItem
{
    tabToRemoveIndex = [tabView indexOfTabViewItem:aTabViewItem];
}

- (void)tabView:(NSTabView *)aTabView didCloseTabViewItem:(NSTabViewItem *)aTabViewItem
{
    [[self py] closePaneAtIndex:tabToRemoveIndex];
}

- (void)tabView:(NSTabView *)aTabView didSelectTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    if (index >= 0) {
        [[self py] setSelectedAccountIndex:index];
    }
}

/* Python callbacks */

- (void)close
{
    [window orderOut:self];
}

- (void)closeSelectedTab
{
    // We must send the setSelectedAccountIndex *only* once the tab is gone, that is why we play 
    // with the delegate like this. Don't forget that it's the tabBar that has self as delegate
    // tabView has tabBar as delegate
    [tabBar setDelegate:nil];
    [tabView removeTabViewItem:[tabView selectedTabViewItem]];
    [tabBar setDelegate:self];
    if ([tabView selectedTabViewItem] != nil) {
        [self tabView:tabView didSelectTabViewItem:[tabView selectedTabViewItem]];
    }
}

- (void)refreshTabs
{
    while ([tabView numberOfTabViewItems]) {
        [tabView removeTabViewItem:[tabView tabViewItemAtIndex:0]];
    }
    for (NSInteger i=0; i<[[self py] numberOfAccounts]; i++) {
        NSString *name = [[self py] accountNameAtIndex:i];
        NSTabViewItem *item = [[[NSTabViewItem alloc] initWithIdentifier:name] autorelease];
        [item setLabel:name];
        [item setView:mainView];
        [tabView addTabViewItem:item];
        PSMTabBarCell *cell = [tabBar cellAtIndex:i];
        [cell setCount:[[self py] accountCountAtIndex:i]];
    }
}

- (void)refreshTargetAccounts
{
    [targetAccountsPopup removeAllItems];
    [targetAccountsPopup addItemsWithTitles:[[self py] targetAccountNames]];
}

- (void)show
{
    [window makeKeyAndOrderFront:self];
}

- (void)updateSelectedPane
{
    [targetAccountsPopup selectItemAtIndex:[[self py] selectedTargetAccountIndex]];
    [importTable updateOneOrTwoSided];
    [swapButton setEnabled:[[self py] canPerformSwap]];
}

@end