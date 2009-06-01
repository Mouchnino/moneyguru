#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGGraph.h"
#import "MGLineGraphView.h"
#import "PyBalanceGraph.h"


@interface MGBalanceGraph : MGGraph {}
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName;
@end
