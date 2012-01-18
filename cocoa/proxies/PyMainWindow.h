/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUIContainer.h"
#import "MGConst.h"
#import "PySearchField.h"
#import "PyDateRangeSelector.h"
#import "PyLookup.h"
#import "PyAccountPanel.h"
#import "PyTransactionPanel.h"
#import "PyMassEditionPanel.h"
#import "PyBudgetPanel.h"
#import "PySchedulePanel.h"
#import "PyCustomDateRangePanel.h"
#import "PyAccountReassignPanel.h"
#import "PyExportPanel.h"
#import "PyNetWorthView.h"
#import "PyProfitView.h"
#import "PyTransactionView.h"
#import "PyAccountView.h"
#import "PyScheduleView.h"
#import "PyBudgetView.h"
#import "PyCashculatorView.h"
#import "PyGeneralLedgerView.h"
#import "PyDocPropsView.h"
#import "PyEmptyView.h"

@interface PyMainWindow : PyGUIContainer {}
- (PySearchField *)searchField;
- (PyDateRangeSelector *)daterangeSelector;
- (PyLookup *)accountLookup;
- (PyLookup *)completionLookup;

- (PyAccountPanel *)accountPanel;
- (PyTransactionPanel *)transactionPanel;
- (PyMassEditionPanel *)massEditPanel;
- (PyBudgetPanel *)budgetPanel;
- (PySchedulePanel *)schedulePanel;
- (PyCustomDateRangePanel *)customDateRangePanel;
- (PyAccountReassignPanel *)accountReassignPanel;
- (PyExportPanel *)exportPanel;

- (PyNetWorthView *)nwview;
- (PyProfitView *)pview;
- (PyTransactionView *)tview;
- (PyAccountView *)aview;
- (PyScheduleView *)scview;
- (PyBudgetView *)bview;
- (PyCashculatorView *)ccview;
- (PyGeneralLedgerView *)glview;
- (PyDocPropsView *)dpview;
- (PyEmptyView *)emptyview;

// Navigation
- (void)selectNextView;
- (void)selectPreviousView;
- (NSInteger)currentPaneIndex;
- (void)setCurrentPaneIndex:(NSInteger)index;
- (NSInteger)paneCount;
- (NSString *)paneLabelAtIndex:(NSInteger)index;
- (NSInteger)paneTypeAtIndex:(NSInteger)index;
- (void)showPaneOfType:(NSInteger)paneType;
- (void)closePaneAtIndex:(NSInteger)index;
- (void)movePaneAtIndex:(NSInteger)paneIndex toIndex:(NSInteger)destIndex;
- (void)newTab;
- (void)showAccount;
- (void)navigateBack;
- (void)jumpToAccount;
- (void)toggleAreaVisibility:(NSInteger)area; // MGPaneArea*

// Item Management
- (void)deleteItem;
- (void)duplicateItem;
- (void)editItem;
- (void)makeScheduleFromSelected;
- (void)moveDown;
- (void)moveUp;
- (void)newGroup;
- (void)newItem;

// Other
- (void)export;
- (NSString *)statusLine;
- (NSArray *)hiddenAreas;

// Column menu
- (NSArray *)columnMenuItems;
- (void)toggleColumnMenuItemAtIndex:(NSInteger)index;
@end