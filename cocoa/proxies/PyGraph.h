/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyChart.h"

@interface PyGraph : PyChart {}
// I'm not sure how to have a CGFloat like signature on the py side or if it's possible.
- (CGFloat)xMin;
- (CGFloat)xMax;
- (CGFloat)yMin;
- (CGFloat)yMax;
- (CGFloat)xToday;
- (NSArray *)xLabels;
- (NSArray *)xTickMarks;
- (NSArray *)yLabels;
- (NSArray *)yTickMarks;
@end