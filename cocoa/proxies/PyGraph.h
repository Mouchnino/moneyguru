/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PyChart.h"

@interface PyGraph : PyChart {}
// I'm not sure how to have a CGFloat like signature on the py side or if it's possible.
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