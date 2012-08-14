/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGMainWindowController.h"
#import "MGConst.h"
#import "MGAccountView.h"
#import "MGNetWorthView.h"
#import "MGProfitView.h"
#import "MGTransactionView.h"
#import "MGScheduleView.h"
#import "MGBudgetView.h"
#import "MGGeneralLedgerView.h"
#import "MGCashculatorView.h"
#import "MGDocPropsView.h"
#import "MGEmptyView.h"
#import "MGReadOnlyPluginView.h"
#import "HSPyUtil.h"
#import "Utils.h"

@implementation MGMainWindowController
- (id)initWithDocument:(PyDocument *)document
{
    self = [super initWithWindowNibName:@"MainWindow"];
    model = [[PyMainWindow alloc] initWithDocument:[document pyRef]];
    /*  WEIRD CRASH ALERT
        The window retain call below results in a memory leak. That's bad, but it's always better
        than a crash. Without this retain below, I was getting crashes (at random points in the
        initialization process). To reproduce the crash, all I had to do was to do "New Document"
        and then "Close Document" about 6-7 times.
    */
    [[self window] retain];
    /* Put a cute iTunes-like bottom bar */
    [[self window] setContentBorderThickness:28 forEdge:NSMinYEdge];
    accountProperties = [[MGAccountProperties alloc] initWithParent:self];
    transactionPanel = [[MGTransactionInspector alloc] initWithParent:self];
    massEditionPanel = [[MGMassEditionPanel alloc] initWithParent:self];
    schedulePanel = [[MGSchedulePanel alloc] initWithParent:self];
    budgetPanel = [[MGBudgetPanel alloc] initWithParent:self];
    exportPanel = [[MGExportPanel alloc] initWithParent:self];
    searchField = [[MGSearchField alloc] initWithPyRef:[[self model] searchField]];
    importWindow = [[MGImportWindow alloc] initWithDocument:document];
    csvOptionsWindow = [[MGCSVImportOptions alloc] initWithDocument:document];
    customDateRangePanel = [[MGCustomDateRangePanel alloc] initWithParent:self];
    accountReassignPanel = [[MGAccountReassignPanel alloc] initWithParent:self];
    accountLookup = [[MGAccountLookup alloc] initWithPyRef:[[self model] accountLookup]];
    completionLookup = [[MGCompletionLookup alloc] initWithPyRef:[[self model] completionLookup]];
    dateRangeSelector = [[MGDateRangeSelector alloc] initWithPyRef:[[self model] daterangeSelector]];
    subviews = [[NSMutableArray alloc] init];
    
    // Setup the toolbar
    NSToolbar *toolbar = [[[NSToolbar alloc] initWithIdentifier:MGMainToolbarIdentifier] autorelease];
    [toolbar setDisplayMode:NSToolbarDisplayModeIconOnly];
    [toolbar setAllowsUserCustomization:YES];
    [toolbar setAutosavesConfiguration:YES];
    [toolbar setDelegate:self];
    [[self window] setToolbar:toolbar];
    
    [model bindCallback:createCallback(@"MainWindowView", self)];
    /* Don't set the delegate in the XIB or else delegates methods are called too soon and cause
       crashes.
    */
    [tabBar setShowAddTabButton:YES];
    [tabBar setSizeCellsToFit:YES];
    [tabBar setCellMinWidth:130];
    [tabBar setDelegate:self];
    [[tabBar addTabButton] setTarget:self];
    [[tabBar addTabButton] setAction:@selector(newTab:)];
    
    [[self window] setDelegate:self];
    return self;
}

- (void)dealloc
{
    [[self window] setDelegate:nil];
    [transactionPanel release];
    [massEditionPanel release];
    [schedulePanel release];
    [accountProperties release];
    [budgetPanel release];
    [exportPanel release];
    [searchField release];
    [importWindow release];
    [csvOptionsWindow release];
    [customDateRangePanel release];
    [accountReassignPanel release];
    [accountLookup release];
    [completionLookup release];
    [dateRangeSelector release];
    [subviews release];
    [model release];
    [super dealloc];
}

- (PyMainWindow *)model
{
    return (PyMainWindow *)model;
}

/* Private */
- (BOOL)validateAction:(SEL)action
{
    if ((action == @selector(newGroup:)) || (action == @selector(toggleExcluded:)))
        return [top isKindOfClass:[MGNetWorthView class]] || [top isKindOfClass:[MGProfitView class]];
    else if ((action == @selector(moveUp:)) ||
             (action == @selector(moveDown:)) ||
             (action == @selector(duplicateItem:)) ||
             (action == @selector(makeScheduleFromSelected:)))
        return [top isKindOfClass:[MGTransactionView class]] || [top isKindOfClass:[MGAccountView class]];
    else if (action == @selector(toggleEntriesReconciled:))
        return [top isKindOfClass:[MGAccountView class]] && [(MGAccountView *)top inReconciliationMode];
    else if (action == @selector(showNextView:))
        return [[self model] currentPaneIndex] < [[self model] paneCount]-1;
    else if (action == @selector(showPreviousView:))
        return [[self model] currentPaneIndex] > 0;
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
        return [[dateRangeSelector model] canNavigate];
    return YES;
}

- (NSMenu *)buildColumnsMenu
{
    NSArray *menuItems = [[self model] columnMenuItems];
    if (menuItems == nil) {
        return nil;
    }
    NSMenu *m = [[NSMenu alloc] initWithTitle:@""];
    for (NSInteger i=0; i < [menuItems count]; i++) {
        NSArray *pair = [menuItems objectAtIndex:i];
        NSString *display = [pair objectAtIndex:0];
        BOOL marked = n2b([pair objectAtIndex:1]);
        NSMenuItem *mi = [m addItemWithTitle:display action:@selector(columnMenuClick:) keyEquivalent:@""];
        [mi setTarget:self];
        [mi setState:marked ? NSOnState : NSOffState];
        [mi setTag:i];
    }
    return [m autorelease];
}

- (MGBaseView *)viewFromPaneType:(NSInteger)paneType modelRef:(PyObject *)modelRef
{
    if (paneType == MGPaneTypeNetWorth) {
        return [[[MGNetWorthView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeProfit) {
        return [[[MGProfitView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeTransaction) {
        return [[[MGTransactionView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeAccount) {
        return [[[MGAccountView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeSchedule) {
        return [[[MGScheduleView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeBudget) {
        return [[[MGBudgetView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeCashculator) {
        return [[[MGCashculatorView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeGeneralLedger) {
        return [[[MGGeneralLedgerView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeDocProps) {
        return [[[MGDocPropsView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeEmpty) {
        return [[[MGEmptyView alloc] initWithPyRef:modelRef] autorelease];
    }
    else if (paneType == MGPaneTypeReadOnlyTablePlugin) {
        return [[[MGReadOnlyPluginView alloc] initWithPyRef:modelRef] autorelease];
    }
    else {
        return nil;
    }
}

/* Actions */
- (IBAction)columnMenuClick:(id)sender
{
    NSMenuItem *mi = (NSMenuItem *)sender;
    NSInteger index = [mi tag];
    [[self model] toggleColumnMenuItemAtIndex:index];
}

- (IBAction)delete:(id)sender
{
    [[self model] deleteItem];
}

- (IBAction)duplicateItem:(id)sender
{
    [[self model] duplicateItem];
}

- (IBAction)editItemInfo:(id)sender
{
    [[self model] editItem];
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
    [[self model] jumpToAccount];
}

- (IBAction)makeScheduleFromSelected:(id)sender
{
    [[self model] makeScheduleFromSelected];
}

- (IBAction)moveSelectionDown:(id)sender
{
    [[self model] moveDown];
}

- (IBAction)moveSelectionUp:(id)sender
{
    [[self model] moveUp];
}

- (IBAction)navigateBack:(id)sender
{
    [[self model] navigateBack];
}

- (IBAction)newGroup:(id)sender
{
    [[self model] newGroup];
}

- (IBAction)newItem:(id)sender
{
    [[self model] newItem];
}

- (IBAction)newTab:(id)sender
{
    [[self model] newTab];
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
    [[self model] showPaneOfType:MGPaneTypeNetWorth];
}

- (IBAction)showIncomeStatement:(id)sender
{
    [[self model] showPaneOfType:MGPaneTypeProfit];
}

- (IBAction)showTransactionTable:(id)sender
{
    [[self model] showPaneOfType:MGPaneTypeTransaction];
}

- (IBAction)showNextView:(id)sender
{
    [[self model] selectNextView];
}

- (IBAction)showPreviousView:(id)sender
{
    [[self model] selectPreviousView];
}

- (IBAction)showSelectedAccount:(id)sender
{
    [[self model] showAccount];
}

- (IBAction)toggleEntriesReconciled:(id)sender
{
    [(MGAccountView *)top toggleReconciled];
}

- (IBAction)toggleExcluded:(id)sender
{
    [(id)top toggleExcluded];
}

- (IBAction)toggleReconciliationMode:(id)sender
{
    [(MGAccountView *)top toggleReconciliationMode];
}

- (IBAction)toggleAreaVisibility:(id)sender
{
    NSSegmentedControl *sc = (NSSegmentedControl *)sender;
    NSInteger index = [sc selectedSegment];
    if (index == 0) {
        [[self model] toggleAreaVisibility:MGPaneAreaBottomGraph];
    }
    else if (index == 1) {
        [[self model] toggleAreaVisibility:MGPaneAreaRightChart];
    }
    else {
        NSMenu *m = [self buildColumnsMenu];
        if (m != nil) {
            NSRect buttonRect = [sc frame];
            CGFloat lastSegmentWidth = [sc widthForSegment:2];
            NSPoint popupPoint = NSMakePoint(NSMaxX(buttonRect)-lastSegmentWidth, NSMaxY(buttonRect));
            [m popUpMenuPositioningItem:nil atLocation:popupPoint inView:[[self window] contentView]];
        }
        /* The segment is going to be automatically toggled if we don't do anything. Untoggle it
           after each click.
        */
        [visibilitySegments setSelected:NO forSegment:2];
    }
}

- (IBAction)toggleGraph:(id)sender
{
    [[self model] toggleAreaVisibility:MGPaneAreaBottomGraph];
}

- (IBAction)togglePieChart:(id)sender
{
    [[self model] toggleAreaVisibility:MGPaneAreaRightChart];
}

- (IBAction)export:(id)sender
{
    [[self model] export];
}

/* Public */

- (MGPrintView *)viewToPrint
{
    return [top viewToPrint];
}

- (NSInteger)openedTabCount
{
    return [[self model] paneCount];
}

- (void)closeActiveTab
{
    [[self model] closePaneAtIndex:[[self model] currentPaneIndex]];
}

/* Delegate */
- (void)didEndSheet:(NSWindow *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo
{
    [sheet orderOut:nil];
}

- (BOOL)tabView:(NSTabView *)aTabView shouldCloseTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    [[self model] closePaneAtIndex:index];
    /* We never let the tab bar remove the tab itself. It causes all kind of problems with tab
       syncing. A callback will take care of closing the tab manually.
     */
    return NO;
}

- (void)tabView:(NSTabView *)aTabView didSelectTabViewItem:(NSTabViewItem *)aTabViewItem
{
    NSInteger index = [tabView indexOfTabViewItem:aTabViewItem];
    [[self model] setCurrentPaneIndex:index];
}

- (void)tabView:(NSTabView *)aTabView movedTab:(NSTabViewItem *)aTabViewItem fromIndex:(NSInteger)aFrom toIndex:(NSInteger)aTo
{
    [[self model] movePaneAtIndex:aFrom toIndex:aTo];
}

- (void)windowWillClose:(NSNotification *)notification
{
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
    NSInteger index = [[self model] currentPaneIndex];
    [tabView selectTabViewItemAtIndex:index];
    top = [subviews objectAtIndex:index];
    [[self window] makeFirstResponder:[top mainResponder]];
}

- (void)refreshPanes
{
    [tabBar setDelegate:nil];
    NSArray *oldsubviews = subviews;
    subviews = [[NSMutableArray alloc] init];
    NSInteger paneCount = [[self model] paneCount];
    while ([tabView numberOfTabViewItems] > paneCount) {
        NSTabViewItem *item = [tabView tabViewItemAtIndex:paneCount];
        [tabView removeTabViewItem:item];
    }
    
    for (NSInteger i=0; i<paneCount; i++) {
        NSString *label = [[self model] paneLabelAtIndex:i];
        PyObject *viewRef = [[self model] paneViewRefAtIndex:i];
        MGBaseView *view = nil;
        for (MGBaseView *v in [subviews arrayByAddingObjectsFromArray:oldsubviews]) {
            if ([[v model] modelRef] == viewRef) {
                view = v;
                break;
            }
        }
        if (view == nil) {
            NSInteger paneType = [[self model] paneTypeAtIndex:i];
            view = [self viewFromPaneType:paneType modelRef:viewRef];
        }
        NSImage *tabIcon = [NSImage imageNamed:[view tabIconName]];
        [subviews addObject:view];
        NSTabViewItem *item;
        if (i < [tabView numberOfTabViewItems]) {
            item = [tabView tabViewItemAtIndex:i];
            [item setLabel:label];
            [item setView:[view view]];
        }
        else {
            item = [[[NSTabViewItem alloc] initWithIdentifier:nil] autorelease];
            [item setLabel:label];
            [item setView:[view view]];
            [tabView addTabViewItem:item];
        }
        /* We use cellForTab instead of cellAtIndex because in some cases (just after a move, for
           instance), the cells are not in sync with the tab items so the indexes might not match.
        */
        PSMTabBarCell *tabCell = [tabBar cellForTab:item];
        [tabCell setIcon:tabIcon];
    }
    [oldsubviews release];
    [tabBar setDelegate:self];
}

- (void)refreshStatusLine
{
    [statusLabel setStringValue:[[self model] statusLine]];
}

- (void)refreshUndoActions
{
    [[self window] setDocumentEdited:[[self document] isDocumentEdited]];
}

- (void)showMessage:(NSString *)aMessage
{
    NSAlert *a = [NSAlert alertWithMessageText:aMessage defaultButton:nil alternateButton:nil
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[self window] modalDelegate:nil didEndSelector:nil contextInfo:nil];
}

- (void)updateAreaVisibility
{
    NSIndexSet *hiddenAreas = [Utils array2IndexSet:[[self model] hiddenAreas]];
    BOOL selected = ![hiddenAreas containsIndex:MGPaneAreaBottomGraph];
    [visibilitySegments setSelected:selected forSegment:0];
    selected = ![hiddenAreas containsIndex:MGPaneAreaRightChart];
    [visibilitySegments setSelected:selected forSegment:1];
}

- (void)viewClosedAtIndex:(NSInteger)index
{
    NSTabViewItem *item = [tabView tabViewItemAtIndex:index];
    [subviews removeObjectAtIndex:index];
    [tabView removeTabViewItem:item];
}
@end
