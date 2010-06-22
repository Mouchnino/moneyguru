/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGMainWindowController.h"
#import "Utils.h"
#import "MGConst.h"

@implementation MGMainWindowController
- (id)initWithDocument:(MGDocument *)document
{
    self = [super initWithNibName:@"MainWindow" pyClassName:@"PyMainWindow" pyParent:[document py]];
    [self setDocument:document];
    /* Put a cute iTunes-like bottom bar */
    [[self window] setContentBorderThickness:28 forEdge:NSMinYEdge];
    [self restoreState];
    accountProperties = [[MGAccountProperties alloc] initWithParent:self];
    transactionPanel = [[MGTransactionInspector alloc] initWithParent:self];
    massEditionPanel = [[MGMassEditionPanel alloc] initWithParent:self];
    schedulePanel = [[MGSchedulePanel alloc] initWithParent:self];
    budgetPanel = [[MGBudgetPanel alloc] initWithParent:self];
    netWorthView = [[MGNetWorthView alloc] initWithPyParent:py];
    profitView = [[MGProfitView alloc] initWithPyParent:py];
    transactionView = [[MGTransactionView alloc] initWithPyParent:py];
    accountView = [[MGAccountView alloc] initWithPyParent:py];
    scheduleView = [[MGScheduleView alloc] initWithPyParent:py];
    budgetView = [[MGBudgetView alloc] initWithPyParent:py];
    emptyView = [[MGEmptyView alloc] initWithPyParent:py];
    searchField = [[MGSearchField alloc] initWithPyParent:py];
    importWindow = [[MGImportWindow alloc] initWithDocument:document];
    [importWindow connect];
    csvOptionsWindow = [[MGCSVImportOptions alloc] initWithDocument:document];
    [csvOptionsWindow connect];
    customDateRangePanel = [[MGCustomDateRangePanel alloc] initWithParent:self];
    accountReassignPanel = [[MGAccountReassignPanel alloc] initWithParent:self];
    accountLookup = [[MGAccountLookup alloc] initWithPyParent:py];
    completionLookup = [[MGCompletionLookup alloc] initWithPyParent:py];
    dateRangeSelector = [[MGDateRangeSelector alloc] initWithPyParent:py];
    subviews = [[NSMutableArray alloc] init];
    
    // Setup the toolbar
    NSToolbar *toolbar = [[[NSToolbar alloc] initWithIdentifier:MGMainToolbarIdentifier] autorelease];
    [toolbar setDisplayMode:NSToolbarDisplayModeIconOnly];
    [toolbar setAllowsUserCustomization:YES];
    [toolbar setAutosavesConfiguration:YES];
    [toolbar setDelegate:self];
    [[self window] setToolbar:toolbar];
    
    NSArray *children = [NSArray arrayWithObjects:[netWorthView py], [profitView py],
        [transactionView py], [accountView py], [scheduleView py], [budgetView py],
        [emptyView py], [accountProperties py], [transactionPanel py],  [massEditionPanel py],
        [schedulePanel py], [budgetPanel py], [customDateRangePanel py], [accountReassignPanel py],
        [accountLookup py], [completionLookup py], [dateRangeSelector py], nil];
    [[self py] setChildren:children];
    [[self py] connect];
    [searchField connect];
    /* Don't set the delegate in the XIB or else delegates methods are called to soon and cause
       crashes.
    */
    [tabBar setShowAddTabButton:YES];
    [tabBar setSizeCellsToFit:YES];
    [tabBar setDelegate:self];
    [[tabBar addTabButton] setTarget:self];
    [[tabBar addTabButton] setAction:@selector(newTab:)];
    return self;
}

- (void)dealloc
{
    [transactionPanel release];
    [massEditionPanel release];
    [schedulePanel release];
    [accountProperties release];
    [netWorthView release];
    [profitView release];
    [accountView release];
    [transactionView release];
    [scheduleView release];
    [budgetView release];
    [emptyView release];
    [searchField release];
    [importWindow release];
    [csvOptionsWindow release];
    [customDateRangePanel release];
    [accountReassignPanel release];
    [accountLookup release];
    [dateRangeSelector release];
    [subviews release];
    [super dealloc];
}

- (PyMainWindow *)py
{
    return (PyMainWindow *)py;
}

- (MGDocument *)document
{
    return (MGDocument *)[super document];
}

/* Private */
- (BOOL)validateAction:(SEL)action
{
    if (action == @selector(newGroup:))
        return [top isKindOfClass:[MGNetWorthView class]] || [top isKindOfClass:[MGProfitView class]];
    else if ((action == @selector(moveUp:)) ||
             (action == @selector(moveDown:)) ||
             (action == @selector(duplicateItem:)) ||
             (action == @selector(makeScheduleFromSelected:)))
        return [top isKindOfClass:[MGTransactionView class]] || [top isKindOfClass:[MGAccountView class]];
    else if (action == @selector(toggleEntriesReconciled:))
        return [top isKindOfClass:[MGAccountView class]] && [(MGAccountView *)top inReconciliationMode];
    else if (action == @selector(showNextView:))
        return [[self py] currentPaneIndex] < [[self py] paneCount]-1;
    else if (action == @selector(showPreviousView:))
        return [[self py] currentPaneIndex] > 0;
    else if (action == @selector(showSelectedAccount:)) {
        if ([top isKindOfClass:[MGNetWorthView class]] || [top isKindOfClass:[MGProfitView class]])
            return [(id)top canShowSelectedAccount];
        else
            return [top isKindOfClass:[MGTransactionView class]] || [top isKindOfClass:[MGAccountView class]];
    }
    else if (action == @selector(navigateBack:))
        return [top isKindOfClass:[MGAccountView class]];
    else if (action == @selector(toggleReconciliationMode:))
        return [top isKindOfClass:[MGAccountView class]] && [(MGAccountView *)top canToggleReconciliationMode];
    else if ((action == @selector(selectPrevDateRange:)) || (action == @selector(selectNextDateRange:))
        || (action == @selector(selectTodayDateRange:)))
        return [[dateRangeSelector py] canNavigate];
    return YES;
}


/* Actions */
- (IBAction)delete:(id)sender
{
    [[self py] deleteItem];
}

- (IBAction)duplicateItem:(id)sender
{
    [[self py] duplicateItem];
}

- (IBAction)editItemInfo:(id)sender
{
    [[self py] editItem];
}

- (IBAction)itemSegmentClicked:(id)sender
{
    NSInteger index = [(NSSegmentedControl *)sender selectedSegment];
    if (index == 0) {
        [self newItem:sender];
    }
    else if (index == 1) {
        [self delete:sender];
    }
    else if (index == 2) {
        [self editItemInfo:sender];
    }
}

- (IBAction)jumpToAccount:(id)sender
{
    [[self py] jumpToAccount];
}

- (IBAction)makeScheduleFromSelected:(id)sender
{
    [[self py] makeScheduleFromSelected];
}

- (IBAction)moveDown:(id)sender
{
    [[self py] moveDown];
}

- (IBAction)moveUp:(id)sender
{
    [[self py] moveUp];
}

- (IBAction)navigateBack:(id)sender
{
    [[self py] navigateBack];
}

- (IBAction)newGroup:(id)sender
{
    [[self py] newGroup];
}

- (IBAction)newItem:(id)sender
{
    [[self py] newItem];
}

- (IBAction)newTab:(id)sender
{
    [[self py] newTab];
}

- (IBAction)search:(id)sender
{
    [[self window] makeFirstResponder:[searchField view]];
}

- (IBAction)selectMonthRange:(id)sender
{
    [dateRangeSelector selectMonthRange:sender];
}

- (IBAction)selectNextDateRange:(id)sender
{
    [dateRangeSelector selectNextDateRange:sender];
}

- (IBAction)selectPrevDateRange:(id)sender
{
    [dateRangeSelector selectPrevDateRange:sender];
}

- (IBAction)selectTodayDateRange:(id)sender
{
    [dateRangeSelector selectTodayDateRange:sender];
}

- (IBAction)selectQuarterRange:(id)sender
{
    [dateRangeSelector selectQuarterRange:sender];
}

- (IBAction)selectYearRange:(id)sender
{
    [dateRangeSelector selectYearRange:sender];
}

- (IBAction)selectYearToDateRange:(id)sender
{
    [dateRangeSelector selectYearToDateRange:sender];
}

- (IBAction)selectRunningYearRange:(id)sender
{
    [dateRangeSelector selectRunningYearRange:sender];
}

- (IBAction)selectAllTransactionsRange:(id)sender
{
    [dateRangeSelector selectAllTransactionsRange:sender];
}

- (IBAction)selectCustomDateRange:(id)sender
{
    [dateRangeSelector selectCustomDateRange:sender];
}

- (IBAction)selectSavedCustomRange:(id)sender
{
    [dateRangeSelector selectSavedCustomRange:sender];
}

- (IBAction)showBalanceSheet:(id)sender
{
    [[self py] showPaneOfType:MGPaneTypeNetWorth];
}

- (IBAction)showIncomeStatement:(id)sender
{
    [[self py] showPaneOfType:MGPaneTypeProfit];
}

- (IBAction)showTransactionTable:(id)sender
{
    [[self py] showPaneOfType:MGPaneTypeTransaction];
}

- (IBAction)showScheduleTable:(id)sender
{
    [[self py] showPaneOfType:MGPaneTypeSchedule];
}

- (IBAction)showBudgetTable:(id)sender
{
    [[self py] showPaneOfType:MGPaneTypeBudget];
}

- (IBAction)showNextView:(id)sender
{
    [[self py] selectNextView];
}

- (IBAction)showPreviousView:(id)sender
{
    [[self py] selectPreviousView];
}

- (IBAction)showSelectedAccount:(id)sender
{
    [[self py] showAccount];
}

- (IBAction)toggleEntriesReconciled:(id)sender
{
    [(MGAccountView *)top toggleReconciled];
}

- (IBAction)toggleReconciliationMode:(id)sender
{
    [(MGAccountView *)top toggleReconciliationMode];
}

/* Public */

- (void)restoreState
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    NSString *frameData = [ud stringForKey:@"MainWindowFrame"];
    if (frameData != nil)
    {
        NSRect frame = NSRectFromString(frameData);
        [[self window] setFrame:frame display:YES];
    }
}

- (void)saveState
{
    NSRect f = [[self window] frame];
    NSString *frameData = NSStringFromRect(f);
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    [ud setValue:frameData forKey:@"MainWindowFrame"];
}

- (MGPrintView *)viewToPrint
{
    return [top viewToPrint];
}

- (NSInteger)openedTabCount
{
    return [[self py] paneCount];
}

- (void)closeActiveTab
{
    [[self py] closePaneAtIndex:[[self py] currentPaneIndex]];
}

/* Delegate */
- (void)didEndSheet:(NSWindow *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo
{
    [sheet orderOut:nil];
}

- (BOOL)tabView:(NSTabView *)aTabView shouldCloseTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    [[self py] closePaneAtIndex:index];
    /* We never let the tab bar remove the tab itself. It causes all kind of problems with tab
       syncing. A callback will take care of closing the tab manually.
     */
    return NO;
}

- (void)tabView:(NSTabView *)aTabView didSelectTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    [[self py] setCurrentPaneIndex:index];
}

- (void)tabView:(NSTabView *)aTabView movedTab:(NSTabViewItem *)aTabViewItem fromIndex:(NSInteger)aFrom toIndex:(NSInteger)aTo
{
    [[self py] movePaneAtIndex:aFrom toIndex:aTo];
}

- (void)windowWillClose:(NSNotification *)notification
{
    [self saveState];
    [tabBar setDelegate:nil];
}

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ([top respondsToSelector:@selector(fieldEditorForObject:)]) {
        return [(id)top fieldEditorForObject:asker];
    }
    return nil;
}

/* Toolbar delegate */
- (NSArray *)toolbarAllowedItemIdentifiers:(NSToolbar *)toolbar
{
    return [NSArray arrayWithObjects:
            NSToolbarSpaceItemIdentifier,
            NSToolbarFlexibleSpaceItemIdentifier, 
            MGDateRangeToolbarItemIdentifier,
            MGSearchFieldToolbarItemIdentifier, 
            MGBalanceSheetToolbarItemIdentifier,
            MGIncomeStatementToolbarItemIdentifier,
            MGTransactionsToolbarItemIdentifier,
            MGSchedulesToolbarItemIdentifier,
            MGBudgetToolbarItemIdentifier,
            nil];
}

- (NSArray *)toolbarDefaultItemIdentifiers:(NSToolbar *)toolbar
{
    return [NSArray arrayWithObjects:
            NSToolbarSpaceItemIdentifier,
            NSToolbarFlexibleSpaceItemIdentifier,
            MGDateRangeToolbarItemIdentifier,
            NSToolbarFlexibleSpaceItemIdentifier,
            MGSearchFieldToolbarItemIdentifier,
            nil];
}

- (NSToolbarItem *)toolbar:(NSToolbar *)toolbar itemForItemIdentifier:(NSString *)itemIdentifier 
 willBeInsertedIntoToolbar:(BOOL)inserted
{
    NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
    if ([itemIdentifier isEqual:MGSearchFieldToolbarItemIdentifier]) {
        [toolbarItem setLabel: TR(@"Filter")];
        [toolbarItem setView:[searchField view]];
        [toolbarItem setMinSize:[[searchField view] frame].size];
        [toolbarItem setMaxSize:[[searchField view] frame].size];
    }
    else if ([itemIdentifier isEqual:MGDateRangeToolbarItemIdentifier]) {
        [toolbarItem setLabel: TR(@"Date Range")];
        [toolbarItem setView:[dateRangeSelector view]];
        [toolbarItem setMinSize:[[dateRangeSelector view] frame].size];
        [toolbarItem setMaxSize:[[dateRangeSelector view] frame].size];
    }
    else if ([itemIdentifier isEqual:MGBalanceSheetToolbarItemIdentifier])
    {
        [toolbarItem setLabel:TR(@"Net Worth")];
        [toolbarItem setImage:[NSImage imageNamed:@"balance_sheet_48"]];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showBalanceSheet:)];
    }
    else if ([itemIdentifier isEqual:MGIncomeStatementToolbarItemIdentifier])
    {
        [toolbarItem setLabel:TR(@"Profit/Loss")];
        [toolbarItem setImage:[NSImage imageNamed:@"income_statement_48"]];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showIncomeStatement:)];
    }
    else if ([itemIdentifier isEqual:MGTransactionsToolbarItemIdentifier])
    {
        [toolbarItem setLabel:TR(@"Transactions")];
        [toolbarItem setImage:[NSImage imageNamed:@"transaction_table_48"]];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showTransactionTable:)];
    }
    else if ([itemIdentifier isEqual:MGSchedulesToolbarItemIdentifier])
    {
        [toolbarItem setLabel:TR(@"Schedules")];
        [toolbarItem setImage:[NSImage imageNamed:@"schedules_48"]];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showScheduleTable:)];
    }
    else if ([itemIdentifier isEqual:MGBudgetToolbarItemIdentifier])
    {
        [toolbarItem setLabel:TR(@"Budgets")];
        [toolbarItem setImage:[NSImage imageNamed:@"budget_48"]];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showBudgetTable:)];
    }
    else {
        toolbarItem = nil;
    }
    return toolbarItem;
}

- (BOOL)validateMenuItem:(NSMenuItem *)aItem
{
    if ([aItem tag] == MGNewItemMenuItem) {
        NSString *title = TR(@"New Item");
        if ([top isKindOfClass:[MGNetWorthView class]] || [top isKindOfClass:[MGProfitView class]])
            title = TR(@"New Account");
        else if ([top isKindOfClass:[MGTransactionView class]] || [top isKindOfClass:[MGAccountView class]])
            title = TR(@"New Transaction");
        else if ([top isKindOfClass:[MGScheduleView class]])
            title = TR(@"New Schedule");
        else if ([top isKindOfClass:[MGBudgetView class]])
            title = TR(@"New Budget");
        [aItem setTitle:title];
    }
    return [self validateUserInterfaceItem:aItem];
}

- (BOOL)validateUserInterfaceItem:(id < NSValidatedUserInterfaceItem >)aItem
{
    return [self validateAction:[aItem action]];
}

/* Callbacks for python */
- (void)changeSelectedPane
{
    NSInteger index = [[self py] currentPaneIndex];
    [tabView selectTabViewItemAtIndex:index];
    top = [subviews objectAtIndex:index];
    [[self window] makeFirstResponder:[top mainResponder]];
}

- (void)refreshPanes
{
    [tabBar setDelegate:nil];
    [subviews removeAllObjects];
    while ([tabView numberOfTabViewItems] > 0) {
        NSTabViewItem *item = [tabView tabViewItemAtIndex:0];
        [tabView removeTabViewItem:item];
    }
    for (NSInteger i=0; i<[[self py] paneCount]; i++) {
        NSInteger paneType = [[self py] paneTypeAtIndex:i];
        NSString *label = [[self py] paneLabelAtIndex:i];
        MGBaseView *view = nil;
        if (paneType == MGPaneTypeNetWorth) {
            view = netWorthView;
        }
        else if (paneType == MGPaneTypeProfit) {
            view = profitView;
        }
        else if (paneType == MGPaneTypeTransaction) {
            view = transactionView;
        }
        else if (paneType == MGPaneTypeAccount) {
            view = accountView;
        }
        else if (paneType == MGPaneTypeSchedule) {
            view = scheduleView;
        }
        else if (paneType == MGPaneTypeBudget) {
            view = budgetView;
        }
        else if (paneType == MGPaneTypeEmpty) {
            view = emptyView;
        }
        [subviews addObject:view];
        NSTabViewItem *item = [[[NSTabViewItem alloc] initWithIdentifier:nil] autorelease];
        [item setLabel:label];
        [item setView:[view view]];
        [tabView addTabViewItem:item];
    }
    [tabBar setDelegate:self];
}

- (void)refreshStatusLine
{
    [statusLabel setStringValue:[[self py] statusLine]];
}

- (void)showMessage:(NSString *)aMessage
{
    NSAlert *a = [NSAlert alertWithMessageText:aMessage defaultButton:nil alternateButton:nil
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[self window] modalDelegate:nil didEndSelector:nil contextInfo:nil];
}

- (void)viewClosedAtIndex:(NSInteger)index
{
    NSTabViewItem *item = [tabView tabViewItemAtIndex:index];
    [tabView removeTabViewItem:item];
}
@end
