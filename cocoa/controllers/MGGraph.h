#import <Cocoa/Cocoa.h>
#import "MGGraphView.h"
#import "MGDocument.h"
#import "MGChart.h"
#import "PyGraph.h"


@interface MGGraph : MGChart {}
- (MGGraphView *)view;
- (PyGraph *)py;
@end