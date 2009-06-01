#import <Cocoa/Cocoa.h>
#import "MGTableWithSplitsPrint.h"
#import "PyTransactionPrint.h"

@interface MGTransactionPrint : MGTableWithSplitsPrint

- (PyTransactionPrint *)py;
@end