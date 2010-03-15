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
    customDateRangePanel = [[MGCustomDateRangePanel alloc] initWithDocument:document];
    accountReassignPanel = [[MGAccountReassignPanel alloc] initWithDocument:document];
    accountLookup = [[MGAccountLookup alloc] initWithPyParent:py];
    completionLookup = [[MGCompletionLookup alloc] initWithPyParent:py];
    dateRangeSelector = [[MGDateRangeSelector alloc] initWithPyParent:py dateRangeView:dateRangeSelectorView];
    
    // Setup the toolbar
    NSToolbar *toolbar = [[[NSToolbar alloc] initWithIdentifier:MGMainToolbarIdentifier] autorelease];
    [toolbar setDelegate:self];
    [[self window] setToolbar:toolbar];
    
    NSArray *children = [NSArray arrayWithObjects:[netWorthView py], [profitView py],
        [transactionView py], [accountView py], [scheduleView py], [budgetView py],
        [accountProperties py], [transactionPanel py],  [massEditionPanel py], [schedulePanel py],
        [budgetPanel py], [accountLookup py], [completionLookup py], [dateRangeSelector py], nil];
    [[self py] setChildren:children];
    [[self py] connect];
    [searchField connect];
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
    [reconciliationToolbarItem release];
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

- (void)arrangeViews
{
    /* The view indexes below are just the way they *happen* to be in the NIB. This can change when
    the NIB is changed.
    */
    int MAIN_VIEW_INDEX = 1;
    NSView *contentView = [[self window] contentView];
    NSView *mainView = [[contentView subviews] objectAtIndex:MAIN_VIEW_INDEX];
    NSView *topView = [top view];
    [topView setFrame:[mainView frame]];
    [contentView replaceSubview:mainView with:topView];
    [topView setAutoresizingMask:NSViewWidthSizable|NSViewHeightSizable];
    // Each main view has its nextKeyView set to the view that must have fosuc
    [[self window] makeFirstResponder:[[top view] nextKeyView]];
}

- (MGBaseView *)top
{
    return top;
}

- (void)setTop:(MGBaseView *)aTop
{
    top = aTop;
    [self arrangeViews];
}

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
        return (top == netWorthView) || (top == profitView);
    else if ((action == @selector(moveUp:)) ||
             (action == @selector(moveDown:)) ||
             (action == @selector(duplicateItem:)) ||
             (action == @selector(makeScheduleFromSelected:)))
        return (top == transactionView) || (top == accountView);
    else if (action == @selector(toggleEntriesReconciled:))
        return (top == accountView) && [[[self document] py] inReconciliationMode];
    else if (action == @selector(showNextView:))
        return (top != budgetView);
    else if (action == @selector(showPreviousView:))
        return (top != netWorthView);
    else if (action == @selector(showEntryTable:))
        return [[self py] canSelectEntryTable];
    else if (action == @selector(showSelectedAccount:))
    {
        if ((top == netWorthView) || (top == profitView))
            return [(id)top canShowSelectedAccount];
        else
            return (top == transactionView) || (top == accountView);
    }
    else if (action == @selector(navigateBack:))
        return (top == accountView);
    else if (action == @selector(toggleReconciliationMode:))
        return (top == accountView) && [[[self document] py] shownAccountIsBalanceSheet];
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
    [[dateRangeSelector py] selectMonthRange];
}

- (IBAction)selectNextDateRange:(id)sender
{
    [[dateRangeSelector py] selectNextDateRange];
}

- (IBAction)selectPrevDateRange:(id)sender
{
    [[dateRangeSelector py] selectPrevDateRange];
}

- (IBAction)selectTodayDateRange:(id)sender
{
    [[dateRangeSelector py] selectTodayDateRange];
}

- (IBAction)selectQuarterRange:(id)sender
{
    [[dateRangeSelector py] selectQuarterRange];
}

- (IBAction)selectYearRange:(id)sender
{
    [[dateRangeSelector py] selectYearRange];
}

- (IBAction)selectYearToDateRange:(id)sender
{
    [[dateRangeSelector py] selectYearToDateRange];
}

- (IBAction)selectRunningYearRange:(id)sender
{
    [[dateRangeSelector py] selectRunningYearRange];
}

- (IBAction)selectAllTransactionsRange:(id)sender
{
    [[dateRangeSelector py] selectAllTransactionsRange];
}

- (IBAction)selectCustomDateRange:(id)sender
{
    [[dateRangeSelector py] selectCustomDateRange];
}

- (IBAction)showBalanceSheet:(id)sender
{
    [[self py] selectBalanceSheet];
}

- (IBAction)showIncomeStatement:(id)sender
{
    [[self py] selectIncomeStatement];
}

- (IBAction)showTransactionTable:(id)sender
{
    [[self py] selectTransactionTable];
}

- (IBAction)showEntryTable:(id)sender
{
    [[self py] selectEntryTable];
}

- (IBAction)showScheduleTable:(id)sender
{
    [[self py] selectScheduleTable];
}

- (IBAction)showBudgetTable:(id)sender
{
    [[self py] selectBudgetTable];
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
    if ([[[self document] py] inReconciliationMode])
        [accountView toggleReconciled];
}

- (IBAction)toggleReconciliationMode:(id)sender
{
    [[[self document] py] toggleReconciliationMode];
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

- (void)windowWillClose:(NSNotification *)notification
{
    [self saveState];
}

- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if (top == accountView)
        return [accountView fieldEditorForObject:asker];
    else if (top == transactionView)
        return [transactionView fieldEditorForObject:asker];
    return nil;
}

/* Toolbar delegate */
- (NSArray *)toolbarAllowedItemIdentifiers:(NSToolbar *)toolbar
{
    return [NSArray arrayWithObjects:
            NSToolbarFlexibleSpaceItemIdentifier, 
            MGBalanceSheetToolbarItemIdentifier,
            MGIncomeStatementToolbarItemIdentifier,
            MGTransactionsToolbarItemIdentifier,
            MGEntriesToolbarItemIdentifier,
            MGSchedulesToolbarItemIdentifier,
            MGBudgetToolbarItemIdentifier,
            MGDateRangeToolbarItemIdentifier, 
            MGSearchFieldToolbarItemIdentifier, 
            MGReconcileToolbarItemIdentifier,
            nil];
}

- (NSArray *)toolbarDefaultItemIdentifiers:(NSToolbar *)toolbar
{
    return [NSArray arrayWithObjects:
            MGBalanceSheetToolbarItemIdentifier,
            MGIncomeStatementToolbarItemIdentifier,
            MGTransactionsToolbarItemIdentifier,
            MGEntriesToolbarItemIdentifier,
            MGSchedulesToolbarItemIdentifier,
            MGBudgetToolbarItemIdentifier,
            NSToolbarFlexibleSpaceItemIdentifier,
            MGReconcileToolbarItemIdentifier,
            MGSearchFieldToolbarItemIdentifier,
            nil];
}

- (NSArray *)toolbarSelectableItemIdentifiers:(NSToolbar *)toolbar;
{
    return [NSArray arrayWithObjects:MGBalanceSheetToolbarItemIdentifier,
                                     MGIncomeStatementToolbarItemIdentifier,
                                     MGTransactionsToolbarItemIdentifier,
                                     MGEntriesToolbarItemIdentifier, 
                                     MGSchedulesToolbarItemIdentifier,
                                     MGBudgetToolbarItemIdentifier, nil];
}

- (NSToolbarItem *)toolbar:(NSToolbar *)toolbar itemForItemIdentifier:(NSString *)itemIdentifier 
 willBeInsertedIntoToolbar:(BOOL)inserted
{
    if ([itemIdentifier isEqual:MGSearchFieldToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel: @"Filter"];
        [toolbarItem setView:[searchField view]];
        [toolbarItem setMinSize:[[searchField view] frame].size];
        [toolbarItem setMaxSize:[[searchField view] frame].size];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGBalanceSheetToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Net Worth"];
        [toolbarItem setImage:[NSImage imageNamed:@"balance_sheet_48"]];
        [toolbarItem setToolTip:@"Show the Balance Sheet"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showBalanceSheet:)];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGIncomeStatementToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Profit/Loss"];
        [toolbarItem setImage:[NSImage imageNamed:@"income_statement_48"]];
        [toolbarItem setToolTip:@"Show the Income Statement"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showIncomeStatement:)];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGTransactionsToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Transactions"];
        [toolbarItem setImage:[NSImage imageNamed:@"transaction_table_48"]];
        [toolbarItem setToolTip:@"Edit your transactions"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showTransactionTable:)];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGEntriesToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Account"];
        [toolbarItem setImage:[NSImage imageNamed:@"entry_table_48"]];
        [toolbarItem setToolTip:@"Edit the selected account's entries"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showEntryTable:)];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGSchedulesToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Schedules"];
        [toolbarItem setImage:[NSImage imageNamed:@"schedules_48"]];
        [toolbarItem setToolTip:@"Edit your scheduled transactions"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showScheduleTable:)];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGBudgetToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Budgets"];
        [toolbarItem setImage:[NSImage imageNamed:@"budget_48"]];
        [toolbarItem setToolTip:@"Edit your budgets"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(showBudgetTable:)];
        return toolbarItem;
    }
    else if ([itemIdentifier isEqual:MGReconcileToolbarItemIdentifier])
    {
        NSToolbarItem *toolbarItem = [[[NSToolbarItem alloc] initWithItemIdentifier:itemIdentifier] autorelease];
        [toolbarItem setLabel:@"Reconcile"];
        [toolbarItem setImage:[NSImage imageNamed:@"reconcile_48"]];
        [toolbarItem setToolTip:@"Toggle reconciliation mode on and off"];
        [toolbarItem setTarget:self];
        [toolbarItem setAction:@selector(toggleReconciliationMode:)];
        reconciliationToolbarItem = [toolbarItem retain];
        return toolbarItem;
    }
    return nil;
}

- (BOOL)validateMenuItem:(NSMenuItem *)aItem
{
    if ([aItem tag] == MGNewItemMenuItem)
    {
        NSString *title = @"New Item";
        if ((top == netWorthView) || (top == profitView))
            title = @"New Account";
        else if ((top == transactionView) || (top == accountView))
            title = @"New Transaction";
        else if (top == scheduleView)
            title = @"New Schedule";
        else if (top == budgetView)
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
- (void)refreshReconciliationButton
{
    NSString *imageName = [[[self document] py] inReconciliationMode] ? @"reconcile_check_48" : @"reconcile_48";
    [reconciliationToolbarItem setImage:[NSImage imageNamed:imageName]];
}

- (void)showAccountReassignPanel
{
    [accountReassignPanel load];
    [NSApp beginSheet:[accountReassignPanel window] modalForWindow:[self window] modalDelegate:self 
        didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}


- (void)showBalanceSheet
{
    [self setTop:netWorthView];
    [[[self window] toolbar] setSelectedItemIdentifier:MGBalanceSheetToolbarItemIdentifier];
}

- (void)showCustomDateRangePanel
{
    [customDateRangePanel load];
    [NSApp beginSheet:[customDateRangePanel window] modalForWindow:[self window] modalDelegate:self 
        didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (void)showEntryTable
{
    [self setTop:accountView];
    [[[self window] toolbar] setSelectedItemIdentifier:MGEntriesToolbarItemIdentifier];
}

- (void)showIncomeStatement
{
    [self setTop:profitView];
    [[[self window] toolbar] setSelectedItemIdentifier:MGIncomeStatementToolbarItemIdentifier];
}

- (void)showMessage:(NSString *)aMessage
{
    NSAlert *a = [NSAlert alertWithMessageText:aMessage defaultButton:nil alternateButton:nil
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[self window] modalDelegate:nil didEndSelector:nil contextInfo:nil];
}

- (void)showScheduleTable
{
    [self setTop:scheduleView];
    [[[self window] toolbar] setSelectedItemIdentifier:MGSchedulesToolbarItemIdentifier];
}

- (void)showBudgetTable
{
    [self setTop:budgetView];
    [[[self window] toolbar] setSelectedItemIdentifier:MGBudgetToolbarItemIdentifier];
}

- (void)showTransactionTable
{
    [self setTop:transactionView];
    [[[self window] toolbar] setSelectedItemIdentifier:MGTransactionsToolbarItemIdentifier];
}

@end
