#import <Cocoa/Cocoa.h>
#import "PyTableWithDate.h"

@interface PyEntryTable : PyTableWithDate {}
- (BOOL)canEditRow:(int)row;
- (BOOL)canMoveRows:(NSArray *)rows to:(int)position;
- (BOOL)canReconcileEntryAtRow:(int)row;
- (BOOL)isBalanceNegativeAtRow:(int)row;
- (void)moveDown;
- (void)moveRows:(NSArray *)rows to:(int)position;
- (void)moveUp;
- (BOOL)shouldShowBalanceColumn;
- (void)toggleReconciled;
- (void)toggleReconciledAtRow:(int)row;
- (NSString *)totals;
@end
