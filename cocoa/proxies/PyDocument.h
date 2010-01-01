/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGUI.h"

@interface PyDocument : PyGUI {}
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

/* Undo */

- (BOOL)canUndo;
- (NSString *)undoDescription;
- (void)undo;
- (BOOL)canRedo;
- (NSString *)redoDescription;
- (void)redo;

/* Misc */
- (void)adjustExampleFile;
- (NSString *)loadFromFile:(NSString *)path; // Returns a non-nil value if it failed
- (void)saveToFile:(NSString *)path;
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
