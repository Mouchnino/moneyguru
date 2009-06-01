#import <Cocoa/Cocoa.h>
#import "MGBarGraphView.h"
#import "MGDocument.h"
#import "MGGraph.h"
#import "PyBarGraph.h"


@interface MGBarGraph : MGGraph {}
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName;
@end
