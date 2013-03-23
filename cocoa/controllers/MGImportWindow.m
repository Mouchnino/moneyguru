/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <PSMTabBarControl/PSMTabBarCell.h>
#import "MGImportWindow.h"
#import "MGImportWindow_UI.h"
#import "HSPyUtil.h"

@implementation MGImportWindow

@synthesize tabBar;
@synthesize tabView;
@synthesize mainView;
@synthesize targetAccountsPopup;
@synthesize switchDateFieldsPopup;
@synthesize applySwapToAllCheckbox;
@synthesize swapButton;
@synthesize importTableView;

- (id)initWithDocument:(PyDocument *)aDocument
{
    self = [super initWithWindow:nil];
    [self setWindow:createMGImportWindow_UI(self)];
    model = [[PyImportWindow alloc] initWithDocument:[aDocument pyRef]];
    importTable = [[MGImportTable alloc] initWithPyRef:[model importTable] view:importTableView];
    swapTypePopUp = [[HSPopUpList alloc] initWithPyRef:[model swapTypeList] popupView:switchDateFieldsPopup];
    [model bindCallback:createCallback(@"ImportWindowView", self)];
    [tabBar setSizeCellsToFit:YES];
    [tabBar setCanCloseOnlyTab:YES];
    return self;
}

- (void)dealloc
{
    [model release];
    [importTable release];
    [swapTypePopUp release];
    [super dealloc];
}

/* NSWindowController Overrides */
- (NSString *)windowFrameAutosaveName
{
    return @"ImportWindow";
}

/* Actions */
- (void)changeTargetAccount
{
    [model setSelectedTargetAccountIndex:[targetAccountsPopup indexOfSelectedItem]];
    [importTable updateOneOrTwoSided];
}

- (void)importSelectedPane
{
    [model importSelectedPane];
}

- (void)switchDateFields
{
    BOOL applyToAll = [applySwapToAllCheckbox state] == NSOnState;
    [model performSwap:applyToAll];
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

- (void)setSwapButtonEnabled:(BOOL)enabled
{
    [swapButton setEnabled:enabled];
}

- (void)show
{
    [[self window] makeKeyAndOrderFront:self];
}

- (void)updateSelectedPane
{
    [targetAccountsPopup selectItemAtIndex:[model selectedTargetAccountIndex]];
    [importTable updateOneOrTwoSided];
}

@end