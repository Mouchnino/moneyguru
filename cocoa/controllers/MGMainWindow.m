/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGMainWindow.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGUtils.h"
#import "NSEventAdditions.h"

@implementation MGMainWindow

/* Overrides */

- (void)awakeFromNib
{
    [self window]; // Ensures that all the outlets are set
    MGDocument *document = [self document];
    [self restoreState];
    
    // We need to instantiate the window components before the window.
    accountProperties = [[MGAccountProperties alloc] initWithDocument:document];
    transactionPanel = [[MGTransactionInspector alloc] initWithDocument:document];
    massEditionPanel = [[MGMassEditionPanel alloc] initWithDocument:document];
    schedulePanel = [[MGSchedulePanel alloc] initWithDocument:document];
    [schedulePanel connect];
    budgetPanel = [[MGBudgetPanel alloc] initWithDocument:document];
    [budgetPanel connect];
    netWorthView = [[MGNetWorthView alloc] initWithDocument:document];
    profitView = [[MGProfitView alloc] initWithDocument:document];
    transactionView = [[MGTransactionView alloc] initWithDocument:document];
    accountView = [[MGAccountView alloc] initWithDocument:document];
    scheduleView = [[MGScheduleView alloc] initWithDocument:document];
    budgetView = [[MGBudgetView alloc] initWithDocument:document];
    searchField = [[MGSearchField alloc] initWithDocument:document];
    importWindow = [[MGImportWindow alloc] initWithDocument:document];
    [importWindow connect];
    csvOptionsWindow = [[MGCSVImportOptions alloc] initWithDocument:document];
    [csvOptionsWindow connect];
    customDateRangePanel = [[MGCustomDateRangePanel alloc] initWithDocument:document];
    accountReassignPanel = [[MGAccountReassignPanel alloc] initWithDocument:document];
    
    // Setup the toolbar
    NSToolbar *toolbar = [[[NSToolbar alloc] initWithIdentifier:MGMainToolbarIdentifier] autorelease];
    [toolbar setDelegate:self];
    [[self window] setToolbar:toolbar];
    
    NSArray *children = [NSArray arrayWithObjects:[netWorthView py], [profitView py],
        [transactionView py], [accountView py], [scheduleView py], [budgetView py],
        [accountProperties py], [transactionPanel py],  [massEditionPanel py], [schedulePanel py],
        [budgetPanel py], nil];
    Class PyMainWindow = [MGUtils classNamed:@"PyMainWindow"];
    py = [[PyMainWindow alloc] initWithCocoa:self pyParent:[document py] children:children];
    [py connect];
    [searchField connect];
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
    [reconciliationToolbarItem release];
    [super dealloc];
}

- (oneway void)release
{
    if ([self retainCount] == 2)
    {
        [py free];
    }
    [super release];
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

- (void)animateDateRange:(BOOL)forward
{
    float PADDING = 3;
    NSRect convertedFrame = [dateRangePopUp convertRect:[dateRangePopUp bounds] toView:[[self window] contentView]];
    convertedFrame.size.width -= PADDING *2;
    convertedFrame.size.height -= PADDING *2;
    convertedFrame.origin.x += PADDING;
    convertedFrame.origin.y += PADDING;
    NSImageView *imageView = [[[NSImageView alloc] initWithFrame:convertedFrame] autorelease];
    [imageView setImageAlignment:forward ? NSImageAlignTopRight : NSImageAlignTopLeft];
    [imageView setImageScaling:NSScaleProportionally];
    [imageView setImage:[NSImage imageNamed:forward ? @"forward_32" : @"backward_32"]];
    [[[self window] contentView] addSubview:imageView positioned:NSWindowAbove relativeTo:nil];
    NSMutableDictionary *animData = [NSMutableDictionary dictionary];
    [animData setObject:imageView forKey:NSViewAnimationTargetKey];
    [animData setObject:NSViewAnimationFadeOutEffect forKey:NSViewAnimationEffectKey];
    NSMutableArray *animations = [NSMutableArray arrayWithObject:animData];
    NSViewAnimation *anim = [[NSViewAnimation alloc] initWithViewAnimations:animations];
    [anim setDuration:0.5];
    [anim setAnimationCurve:NSAnimationLinear];
    [anim setDelegate:self];
    [anim startAnimation];
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
        return [py canSelectEntryTable];
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
        return [py canNavigateDateRange];
    return YES;
}


/* Actions */

- (IBAction)delete:(id)sender
{
    [py deleteItem];
}

- (IBAction)duplicateItem:(id)sender
{
    [py duplicateItem];
}

- (IBAction)editItemInfo:(id)sender
{
    [py editItem];
}

- (IBAction)makeScheduleFromSelected:(id)sender
{
    [py makeScheduleFromSelected];
}

- (IBAction)moveDown:(id)sender
{
    [py moveDown];
}

- (IBAction)moveUp:(id)sender
{
    [py moveUp];
}

- (IBAction)navigateBack:(id)sender
{
    [py navigateBack];
}

- (IBAction)newGroup:(id)sender
{
    [py newGroup];
}

- (IBAction)newItem:(id)sender
{
    [py newItem];
}

- (IBAction)search:(id)sender
{
    [[self window] makeFirstResponder:[searchField view]];
}

- (IBAction)selectMonthRange:(id)sender
{
    [[[self document] py] selectMonthRange];
}

- (IBAction)selectNextDateRange:(id)sender
{
    [[[self document] py] selectNextDateRange];
}

- (IBAction)selectPrevDateRange:(id)sender
{
    [[[self document] py] selectPrevDateRange];
}

- (IBAction)selectTodayDateRange:(id)sender
{
    [[[self document] py] selectTodayDateRange];
}

- (IBAction)selectQuarterRange:(id)sender
{
    [[[self document] py] selectQuarterRange];
}

- (IBAction)selectYearRange:(id)sender
{
    [[[self document] py] selectYearRange];
}

- (IBAction)selectYearToDateRange:(id)sender
{
    [[[self document] py] selectYearToDateRange];
}

- (IBAction)selectRunningYearRange:(id)sender
{
    [[[self document] py] selectRunningYearRange];
}

- (IBAction)selectCustomDateRange:(id)sender
{
    [[[self document] py] selectCustomDateRange];
}

- (IBAction)showBalanceSheet:(id)sender
{
    [py selectBalanceSheet];
}

- (IBAction)showIncomeStatement:(id)sender
{
    [py selectIncomeStatement];
}

- (IBAction)showTransactionTable:(id)sender
{
    [py selectTransactionTable];
}

- (IBAction)showEntryTable:(id)sender
{
    [py selectEntryTable];
}

- (IBAction)showScheduleTable:(id)sender
{
    [py selectScheduleTable];
}

- (IBAction)showBudgetTable:(id)sender
{
    [py selectBudgetTable];
}

- (IBAction)showNextView:(id)sender
{
    [py selectNextView];
}

- (IBAction)showPreviousView:(id)sender
{
    [py selectPreviousView];
}

- (IBAction)showSelectedAccount:(id)sender
{
    [py showAccount];
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
- (void)animationDidEnd:(NSAnimation *)animation
{
    // Remove all views used by the animation from their superviews
    NSDictionary *animData;
    NSEnumerator *e = [[(NSViewAnimation *)animation viewAnimations] objectEnumerator];
    while (animData = [e nextObject])
    {
        NSView *view = [animData objectForKey:NSViewAnimationTargetKey];
        [view removeFromSuperview];
    }
    [animation release];
}

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

- (void)animateDateRangeForward
{
    [self animateDateRange:YES];
}

- (void)animateDateRangeBackward
{
    [self animateDateRange:NO];
}

- (void)refreshDateRangeSelector
{
    [dateRangePopUp setTitle:[[[self document] py] dateRangeDisplay]];
    BOOL canNavigate = [py canNavigateDateRange];
    [prevDateRangeButton setEnabled:canNavigate];
    [nextDateRangeButton setEnabled:canNavigate];
}

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
