#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyDocument : PyGUI {}
/* Views */

- (void)selectBalanceSheet;
- (void)selectIncomeStatement;
- (void)selectTransactionTable;
- (void)selectEntryTable;
- (BOOL)canSelectEntryTable;

/* Date range */
- (void)selectPrevDateRange;
- (void)selectNextDateRange;
- (void)selectTodayDateRange;
- (void)selectMonthRange;
- (void)selectQuarterRange;
- (void)selectYearRange;
- (void)selectYearToDateRange;
- (void)selectRunningYearRange;
- (void)selectCustomDateRange;
- (NSString *)dateRangeDisplay;

/* Reconciliation */
- (void)toggleReconciliationMode;
- (BOOL)inReconciliationMode;
- (void)toggleEntriesReconciled;

/* Undo */

- (BOOL)canUndo;
- (NSString *)undoDescription;
- (void)undo;
- (BOOL)canRedo;
- (NSString *)redoDescription;
- (void)redo;

/* Misc */
- (NSString *)loadFromFile:(NSString *)path; // Returns a non-nil value if it failed
- (NSString *)saveToFile:(NSString *)path;
- (void)saveToQIF:(NSString *)path;
- (NSString *)import:(NSString *)path;
- (BOOL)isDirty;
- (void)stopEdition;
- (int)transactionCount;
- (BOOL)shownAccountIsBalanceSheet;
- (void)close;

// Temporary
- (BOOL)isRegistered;
@end;
