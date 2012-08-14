/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGImportWindow.h"
#import "PSMTabBarCell.h"
#import "HSPyUtil.h"

@implementation MGImportWindow
- (id)initWithDocument:(PyDocument *)aDocument
{
    self = [super initWithWindowNibName:@"ImportWindow"];
    [self window];
    model = [[PyImportWindow alloc] initWithDocument:[aDocument pyRef]];
    importTable = [[MGImportTable alloc] initWithPyRef:[model importTable] view:importTableView];
    [model bindCallback:createCallback(@"ImportWindowView", self)];
    [tabBar setSizeCellsToFit:YES];
    [tabBar setCanCloseOnlyTab:YES];
    return self;
}

- (void)dealloc
{
    [model release];
    [importTable release];
    [super dealloc];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"ImportWindow";
}

/* Actions */
- (IBAction)changeTargetAccount:(id)sender
{
    [model setSelectedTargetAccountIndex:[targetAccountsPopup indexOfSelectedItem]];
    [importTable updateOneOrTwoSided];
}

- (IBAction)importSelectedPane:(id)sender
{
    [model importSelectedPane];
}

- (IBAction)selectSwapType:(id)sender
{
    [model setSwapTypeIndex:[switchDateFieldsPopup indexOfSelectedItem]];
    [swapButton setEnabled:[model canPerformSwap]];
}

- (IBAction)switchDateFields:(id)sender
{
    BOOL applyToAll = [applySwapToAllCheckbox state] == NSOnState;
    if ([model canPerformSwap]) {
        [model performSwap:applyToAll];
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
    [model closePaneAtIndex:tabToRemoveIndex];
}

- (void)tabView:(NSTabView *)aTabView didSelectTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    if (index >= 0) {
        [model setSelectedAccountIndex:index];
    }
}

/* Python callbacks */

- (void)close
{
    [[self window] orderOut:self];
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
    for (NSInteger i=0; i<[model numberOfAccounts]; i++) {
        NSString *name = [model accountNameAtIndex:i];
        NSTabViewItem *item = [[[NSTabViewItem alloc] initWithIdentifier:name] autorelease];
        [item setLabel:name];
        [item setView:mainView];
        [tabView addTabViewItem:item];
        PSMTabBarCell *cell = [tabBar cellAtIndex:i];
        [cell setCount:[model accountCountAtIndex:i]];
    }
}

- (void)refreshTargetAccounts
{
    [targetAccountsPopup removeAllItems];
    [targetAccountsPopup addItemsWithTitles:[model targetAccountNames]];
}

- (void)show
{
    [[self window] makeKeyAndOrderFront:self];
}

- (void)updateSelectedPane
{
    [targetAccountsPopup selectItemAtIndex:[model selectedTargetAccountIndex]];
    [importTable updateOneOrTwoSided];
    [swapButton setEnabled:[model canPerformSwap]];
}

@end