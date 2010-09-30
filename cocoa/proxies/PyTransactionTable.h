/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTableWithDate.h"

@interface PyTransactionTable : PyTableWithDate {}
- (BOOL)isBoldAtRow:(NSInteger)row;
- (BOOL)canMoveRows:(NSArray *)rows to:(NSInteger)position;
- (void)moveRows:(NSArray *)rows to:(NSInteger)position;
- (void)showFromAccount;
- (void)showToAccount;
@end