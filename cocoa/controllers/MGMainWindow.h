/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGAccountProperties.h"
#import "MGTransactionInspector.h"
#import "MGMassEditionPanel.h"
#import "MGEntryTable.h"
#import "MGBalanceSheet.h"
#import "MGIncomeStatement.h"
#import "MGTransactionTable.h"
#import "MGScheduleTable.h"
#import "MGSearchField.h"
#import "MGImportWindow.h"
#import "MGCSVImportOptions.h"
#import "MGCustomDateRangePanel.h"
#import "MGAccountReassignPanel.h"
#import "MGGUIController.h"
#import "MGPrintView.h"
#import "PyMainWindow.h"

@interface MGMainWindow : NSWindowController
{
    IBOutlet NSPopUpButton *dateRangePopUp;
    IBOutlet NSButton *prevDateRangeButton;
    IBOutlet NSButton *nextDateRangeButton;

    PyMainWindow *py;
    MGAccountProperties *accountProperties;
    MGTransactionInspector *transactionPanel;
    MGMassEditionPanel *massEditionPanel;
    MGBalanceSheet *balanceSheet;
    MGIncomeStatement *incomeStatement;
    MGTransactionTable *transactionTable;
    MGEntryTable *entryTable;
    MGScheduleTable *scheduleTable;
    MGSearchField *searchField;
    MGImportWindow *importWindow;
    MGCSVImportOptions *csvOptionsWindow;
    MGCustomDateRangePanel *customDateRangePanel;
    MGAccountReassignPanel *accountReassignPanel;
    MGGUIController *top;
    NSToolbarItem *reconciliationToolbarItem;
}

/* Private */
- (void)arrangeViews;
- (MGGUIController *)top;
- (void)setTop:(MGGUIController *)top;
- (void)animateDateRange:(BOOL)forward;

/* Actions */
- (IBAction)delete:(id)sender;
- (IBAction)editItemInfo:(id)sender;
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
- (IBAction)selectCustomDateRange:(id)sender;
- (IBAction)showBalanceSheet:(id)sender;
- (IBAction)showIncomeStatement:(id)sender;
- (IBAction)showTransactionTable:(id)sender;
- (IBAction)showEntryTable:(id)sender;
- (IBAction)showScheduleTable:(id)sender;
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
