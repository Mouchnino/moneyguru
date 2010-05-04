/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGMainWindow.h"
#import "Utils.h"
#import "MGConst.h"
#import "NSEventAdditions.h"

@implementation MGMainWindow
- (id)initWithDocument:(MGDocument *)document
{
    self = [super initWithNibName:@"MainWindow" pyClassName:@"PyMainWindow" pyParent:[document py]];
    [self setDocument:document];
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
    searchField = [[MGSearchField alloc] initWithPyParent:py];
    importWindow = [[MGImportWindow alloc] initWithDocument:document];
    [importWindow connect];
    csvOptionsWindow = [[MGCSVImportOptions alloc] initWithDocument:document];
    [csvOptionsWindow connect];
    customDateRangePanel = [[MGCustomDateRangePanel alloc] initWithParent:self];
    accountReassignPanel = [[MGAccountReassignPanel alloc] initWithDocument:document];
    accountLookup = [[MGAccountLookup alloc] initWithPyParent:py];
    completionLookup = [[MGCompletionLookup alloc] initWithPyParent:py];
    dateRangeSelector = [[MGDateRangeSelector alloc] initWithPyParent:py];
    subviews = [[NSMutableArray alloc] init];
    
    // Setup the toolbar
    NSToolbar *toolbar = [[[NSToolbar alloc] initWithIdentifier:MGMainToolbarIdentifier] autorelease];
    [toolbar setDisplayMode:NSToolbarDisplayModeIconOnly];
    [toolbar setDelegate:self];
    [[self window] setToolbar:toolbar];
    
    NSArray *children = [NSArray arrayWithObjects:[netWorthView py], [profitView py],
        [transactionView py], [accountView py], [scheduleView py], [budgetView py],
        [accountProperties py], [transactionPanel py],  [massEditionPanel py], [schedulePanel py],
        [budgetPanel py], [customDateRangePanel py], [accountLookup py], [completionLookup py],
        [dateRangeSelector py], nil];
    [[self py] setChildren:children];
    [[self py] connect];
    [searchField connect];
    /* Don't set the delegate in the XIB or else delegates methods are called to soon and cause
       crashes.
    */
    [tabBar setDelegate:self];
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

- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event])
	{
        [super keyDown:event];
	}
}

/* Private */
- (BOOL)dispatchSpecialKeys:(NSEvent *)event
{
    SEL action = nil;
    if ([event modifierKeysFlags] == (NSCommandKeyMask | NSShiftKeyMask))
    {
        if ([event isLeft])
            action = @selector(showPreviousView:);
        else if ([event isRight])
            action = @selector(showNextView:);
    }
    else if ([event modifierKeysFlags] == NSCommandKeyMask)
    {
        if ([event isLeft])
            action = @selector(navigateBack:);
        else if ([event isRight])
            action = @selector(showSelectedAccount:);
    }
    if ((action != nil) && ([self validateAction:action]))
        [self performSelector:action withObject:self];
    return action != nil;
}

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
        return [[self py] currentViewIndex] < [[self py] viewCount]-1;
    else if (action == @selector(showPreviousView:))
        return [[self py] currentViewIndex] > 0;
    else if (action == @selector(showEntryTable:))
        return [[self py] canSelectEntryTable];
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
    [[self py] setCurrentViewIndex:0];
}

- (IBAction)showIncomeStatement:(id)sender
{
    [[self py] setCurrentViewIndex:1];
}

- (IBAction)showTransactionTable:(id)sender
{
    [[self py] setCurrentViewIndex:2];
}

- (IBAction)showEntryTable:(id)sender
{
    [[self py] setCurrentViewIndex:3];
}

- (IBAction)showScheduleTable:(id)sender
{
    [[self py] setCurrentViewIndex:4];
}

- (IBAction)showBudgetTable:(id)sender
{
    [[self py] setCurrentViewIndex:5];
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

/* Delegate */
- (void)didEndSheet:(NSWindow *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo
{
    [sheet orderOut:nil];
}

- (void)tabView:(NSTabView *)aTabView didSelectTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    [[self py] setCurrentViewIndex:index];
}

- (void)windowWillClose:(NSNotification *)notification
{
    [self saveState];
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
    if ([itemIdentifier isEqual:MGSearchFieldToolbarItemIdentifier]) {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel: @"Filter"];
        [toolbarItem setView:[searchField view]];
        [toolbarItem setMinSize:[[searchField view] frame].size];
        [toolbarItem setMaxSize:[[searchField view] frame].size];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGDateRangeToolbarItemIdentifier]) {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel: @"Date Range"];
        [toolbarItem setView:[dateRangeSelector view]];
        [toolbarItem setMinSize:[[dateRangeSelector view] frame].size];
        [toolbarItem setMaxSize:[[dateRangeSelector view] frame].size];
        return toolbarItem;
    }
    return nil;
}

- (BOOL)validateMenuItem:(NSMenuItem *)aItem
{
    if ([aItem tag] == MGNewItemMenuItem) {
        NSString *title = @"New Item";
        if ([top isKindOfClass:[MGNetWorthView class]] || [top isKindOfClass:[MGProfitView class]])
            title = @"New Account";
        else if ([top isKindOfClass:[MGTransactionView class]] || [top isKindOfClass:[MGAccountView class]])
            title = @"New Transaction";
        else if ([top isKindOfClass:[MGScheduleView class]])
            title = @"New Schedule";
        else if ([top isKindOfClass:[MGBudgetView class]])
            title = @"New Budget";
        [aItem setTitle:title];
    }
    return [self validateUserInterfaceItem:aItem];
}

- (BOOL)validateUserInterfaceItem:(id < NSValidatedUserInterfaceItem >)aItem
{
    return [self validateAction:[aItem action]];
}

/* Callbacks for python */
- (void)changeSelectedView
{
    NSInteger index = [[self py] currentViewIndex];
    [tabView selectTabViewItemAtIndex:index];
    top = [subviews objectAtIndex:index];
}

- (void)refreshSubviews
{
    [subviews removeAllObjects];
    while ([tabView numberOfTabViewItems] > 0) {
        NSTabViewItem *item = [tabView tabViewItemAtIndex:0];
        [tabView removeTabViewItem:item];
    }
    for (NSInteger i=0; i<[[self py] viewCount]; i++) {
        enum MGViewType viewType = [[self py] viewTypeAtIndex:i];
        NSString *label = nil;
        MGBaseView *view = nil;
        if (viewType == MGViewTypeNetWorth) {
            label = @"Net Worth";
            view = netWorthView;
        }
        else if (viewType == MGViewTypeProfit) {
            label = @"Profit & Loss";
            view = profitView;
        }
        else if (viewType == MGViewTypeTransaction) {
            label = @"Transactions";
            view = transactionView;
        }
        else if (viewType == MGViewTypeAccount) {
            label = @"Account";
            view = accountView;
        }
        else if (viewType == MGViewTypeSchedule) {
            label = @"Schedules";
            view = scheduleView;
        }
        else if (viewType == MGViewTypeBudget) {
            label = @"Budgets";
            view = budgetView;
        }
        [subviews addObject:view];
        NSTabViewItem *item = [[[NSTabViewItem alloc] initWithIdentifier:nil] autorelease];
        [item setLabel:label];
        [item setView:[view view]];
        [tabView addTabViewItem:item];
    }
}

- (void)showAccountReassignPanel
{
    [accountReassignPanel load];
    [NSApp beginSheet:[accountReassignPanel window] modalForWindow:[self window] modalDelegate:self 
        didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (void)showMessage:(NSString *)aMessage
{
    NSAlert *a = [NSAlert alertWithMessageText:aMessage defaultButton:nil alternateButton:nil
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[self window] modalDelegate:nil didEndSelector:nil contextInfo:nil];
}
@end
