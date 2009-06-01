#import <Cocoa/Cocoa.h>
#import "PyChart.h"

@interface PyGraph : PyChart {}

- (float)xMin;
- (float)xMax;
- (float)yMin;
- (float)yMax;
- (float)xToday;
- (NSArray *)xLabels;
- (NSArray *)xTickMarks;
- (NSArray *)yLabels;
- (NSArray *)yTickMarks;
@end