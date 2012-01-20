/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGPieChart.h"
#import "MGPieChartView.h"

@implementation MGPieChart
- (id)initWithPy:(id)aPy
{
    MGPieChartView *myview = [[MGPieChartView alloc] init];
    self = [super initWithPy:aPy];
    [self setView:[myview autorelease]];
    return self;
}
@end