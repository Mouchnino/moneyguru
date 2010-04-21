/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyMainWindow : PyGUI {}
- (void)setChildren:(NSArray *)children;
// Navigation
- (void)selectBalanceSheet;
- (void)selectIncomeStatement;
- (void)selectTransactionTable;
- (void)selectEntryTable;
- (BOOL)canSelectEntryTable;
- (void)selectScheduleTable;
- (void)selectBudgetTable;
- (void)selectNextView;
- (void)selectPreviousView;
- (NSInteger)currentViewIndex;
- (void)showAccount;
- (void)navigateBack;
- (void)jumpToAccount;

// Item Management
- (void)deleteItem;
- (void)duplicateItem;
- (void)editItem;
- (void)makeScheduleFromSelected;
- (void)moveDown;
- (void)moveUp;
- (void)newGroup;
- (void)newItem;
@end