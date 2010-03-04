/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSWindowController.h"
#import "MGAccountProperties.h"
#import "MGTransactionInspector.h"
#import "MGMassEditionPanel.h"
#import "MGSchedulePanel.h"
#import "MGBudgetPanel.h"
#import "MGAccountView.h"
#import "MGNetWorthView.h"
#import "MGProfitView.h"
#import "MGTransactionView.h"
#import "MGScheduleView.h"
#import "MGBudgetView.h"
#import "MGSearchField.h"
#import "MGImportWindow.h"
#import "MGCSVImportOptions.h"
#import "MGCustomDateRangePanel.h"
#import "MGAccountReassignPanel.h"
#import "MGAccountLookup.h"
#import "MGBaseView.h"
#import "MGPrintView.h"
#import "PyMainWindow.h"

@interface MGMainWindow : HSWindowController
{
    IBOutlet NSPopUpButton *dateRangePopUp;
    IBOutlet NSButton *prevDateRangeButton;
    IBOutlet NSButton *nextDateRangeButton;

    MGAccountProperties *accountProperties;
    MGTransactionInspector *transactionPanel;
    MGMassEditionPanel *massEditionPanel;
    MGSchedulePanel *schedulePanel;
    MGBudgetPanel *budgetPanel;
    MGNetWorthView *netWorthView;
    MGProfitView *profitView;
    MGTransactionView *transactionView;
    MGAccountView *accountView;
    MGScheduleView *scheduleView;
    MGBudgetView *budgetView;
    MGSearchField *searchField;
    MGImportWindow *importWindow;
    MGCSVImportOptions *csvOptionsWindow;
    MGCustomDateRangePanel *customDateRangePanel;
    MGAccountReassignPanel *accountReassignPanel;
    MGAccountLookup *accountLookup;
    MGBaseView *top;
    NSToolbarItem *reconciliationToolbarItem;
}
- (id)initWithDocument:(MGDocument *)document;
- (PyMainWindow *)py;
- (MGDocument *)document;
/* Private */
- (void)arrangeViews;
- (MGBaseView *)top;
- (void)setTop:(MGBaseView *)top;
- (void)animateDateRange:(BOOL)forward;
- (BOOL)dispatchSpecialKeys:(NSEvent *)event;
- (BOOL)validateAction:(SEL)action;

/* Actions */
- (IBAction)delete:(id)sender;
- (IBAction)duplicateItem:(id)sender;
- (IBAction)editItemInfo:(id)sender;
- (IBAction)jumpToAccount:(id)sender;
- (IBAction)makeScheduleFromSelected:(id)sender;
- (IBAction)moveDown:(id)sender;
- (IBAction)moveUp:(id)sender;
- (IBAction)navigateBack:(id)sender;
- (IBAction)newGroup:(id)sender;
- (IBAction)newItem:(id)sender;
- (IBAction)search:(id)sender;
- (IBAction)selectMonthRange:(id)sender;
- (IBAction)selectNextDateRange:(id)sender;
- (IBAction)selectPrevDateRange:(id)sender;
- (IBAction)selectTodayDateRange:(id)sender;
- (IBAction)selectQuarterRange:(id)sender;
- (IBAction)selectYearRange:(id)sender;
- (IBAction)selectYearToDateRange:(id)sender;
- (IBAction)selectRunningYearRange:(id)sender;
- (IBAction)selectAllTransactionsRange:(id)sender;
- (IBAction)selectCustomDateRange:(id)sender;
- (IBAction)showBalanceSheet:(id)sender;
- (IBAction)showIncomeStatement:(id)sender;
- (IBAction)showTransactionTable:(id)sender;
- (IBAction)showEntryTable:(id)sender;
- (IBAction)showScheduleTable:(id)sender;
- (IBAction)showBudgetTable:(id)sender;
- (IBAction)showNextView:(id)sender;
- (IBAction)showPreviousView:(id)sender;
- (IBAction)showSelectedAccount:(id)sender;
- (IBAction)toggleReconciliationMode:(id)sender;
- (IBAction)toggleEntriesReconciled:(id)sender;

/* Public */

- (void)restoreState;
- (void)saveState;
- (MGPrintView *)viewToPrint;

/* Delegate */
- (BOOL)validateMenuItem:(NSMenuItem *)aItem;
- (BOOL)validateUserInterfaceItem:(id < NSValidatedUserInterfaceItem >)aItem;

@end
