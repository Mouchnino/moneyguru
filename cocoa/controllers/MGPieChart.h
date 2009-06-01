#import <Cocoa/Cocoa.h>
#import "MGDocument.h"
#import "MGChart.h"
#import "PyChart.h"

@interface MGPieChart : MGChart {}
- (id)initWithDocument:(MGDocument *)aDocument pieChartClassName:(NSString *)className;
- (PyChart *)py;
@end