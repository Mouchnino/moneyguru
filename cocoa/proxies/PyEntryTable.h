/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTableWithDate.h"

@interface PyEntryTable : PyTableWithDate {}
- (BOOL)canMoveRows:(NSArray *)rows to:(NSInteger)position;
- (BOOL)canReconcileEntryAtRow:(NSInteger)row;
- (BOOL)isBalanceNegativeAtRow:(NSInteger)row;
- (BOOL)isBoldAtRow:(NSInteger)row;
- (void)moveRows:(NSArray *)rows to:(NSInteger)position;
- (BOOL)shouldShowBalanceColumn;
- (void)showTransferAccount;
- (void)toggleReconciled;
- (void)toggleReconciledAtRow:(NSInteger)row;
@end
