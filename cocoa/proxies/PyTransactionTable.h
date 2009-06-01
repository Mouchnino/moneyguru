#import <Cocoa/Cocoa.h>
#import "PyTableWithDate.h"

@interface PyTransactionTable : PyTableWithDate {}

- (BOOL)canMoveRows:(NSArray *)rows to:(int)position;
- (void)moveDown;
- (void)moveRows:(NSArray *)rows to:(int)position;
- (void)moveUp;
- (NSString *)totals;
@end