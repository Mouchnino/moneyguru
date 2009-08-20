/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyTableWithDate.h"

@interface PyTransactionTable : PyTableWithDate {}

- (BOOL)canMoveRows:(NSArray *)rows to:(int)position;
- (void)makeScheduleFromSelected;
- (void)moveDown;
- (void)moveRows:(NSArray *)rows to:(int)position;
- (void)moveUp;
- (NSString *)totals;
@end