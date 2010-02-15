/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
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
    importTable = [[MGImportTable alloc] initWithImportWindow:[self py] view:importTableView];
    importTableOneSided = [[MGImportTableOneSided alloc] initWithImportWindow:[self py] view:importTableOneSidedView];
    [importTableOneSided connect];
    visibleTable = importTableOneSided;
    [importTableOneSidedScrollView setFrame:[importTablePlaceholder frame]]; 
    [mainView replaceSubview:importTablePlaceholder with:importTableOneSidedScrollView];
    return self;
}

- (void)dealloc
{
    [importTable release];
    [importTableOneSided release];
    [super dealloc];
}

- (PyImportWindow *)py
{
    return (PyImportWindow *)py;
}

- (void)updateVisibleTable
{
    // Ok, this code below is a quite hackish. I guess that importTable and importTableOneSided
    // should be a single class that hides columns (like in the PyQt side) rather than doing this
    // kind of fuss around
    if ([(PyImportTable *)[visibleTable py] isTwoSided]) {
        // Show the two sided table
        if (visibleTable == importTable)
            return;
        [importTableOneSided disconnect];
        [importTable connect];
        [importTableScrollView setFrame:[importTableOneSidedScrollView frame]]; 
        [mainView replaceSubview:importTableOneSidedScrollView with:importTableScrollView];
        visibleTable = importTable;
    } else {
        // Show the one sided table
        if (visibleTable == importTableOneSided)
            return;
        [importTable disconnect];
        [importTableOneSided connect];
        [importTableOneSidedScrollView setFrame:[importTableScrollView frame]]; 
        [mainView replaceSubview:importTableScrollView with:importTableOneSidedScrollView];
        visibleTable = importTableOneSided;
    }
}

/* Actions */
- (IBAction)changeTargetAccount:(id)sender
{
    [[self py] setSelectedTargetAccountIndex:[targetAccountsPopup indexOfSelectedItem]];
    [self updateVisibleTable];
}

- (IBAction)importSelectedPane:(id)sender
{
    [[self py] importSelectedPane];
}

- (IBAction)switchDateFields:(id)sender
{
    BOOL applyToAll = [applySwapToAllCheckbox state] == NSOnState;
    NSMenuItem *item = [switchDateFieldsPopup selectedItem];
    if ((item == switchDayMonthMenuItem) && ([[self py] canSwitchDayMonth]))
        [[self py] switchDayMonth:applyToAll];
    else if ((item == switchMonthYearMenuItem) && ([[self py] canSwitchMonthYear]))
        [[self py] switchMonthYear:applyToAll];
    else if ((item == switchDayYearMenuItem) && ([[self py] canSwitchDayYear]))
        [[self py] switchDayYear:applyToAll];
    else if ((item == switchDescriptionPayeeMenuItem))
        [[self py] switchDescriptionPayee:applyToAll];
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
    if (index >= 0)
    {
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
    if ([tabView selectedTabViewItem] != nil)
    {
        [self tabView:tabView didSelectTabViewItem:[tabView selectedTabViewItem]];
    }
}

- (void)refreshTabs
{
    while ([tabView numberOfTabViewItems])
    {
        [tabView removeTabViewItem:[tabView tabViewItemAtIndex:0]];
    }
    for (NSInteger i=0; i<[[self py] numberOfAccounts]; i++)
    {
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
    [self updateVisibleTable];
    [switchDayMonthMenuItem setEnabled:[[self py] canSwitchDayMonth]];
    [switchMonthYearMenuItem setEnabled:[[self py] canSwitchMonthYear]];
    [switchDayYearMenuItem setEnabled:[[self py] canSwitchDayYear]];
}

@end