#import <Cocoa/Cocoa.h>
#import "PyPrintView.h"

@interface PySplitPrint : PyPrintView {}
- (int)splitCountAtRow:(int)aRow;
// returns [account, memo, amount]
- (NSArray *)splitValuesAtRow:(int)row splitRow:(int)splitRow;
@end