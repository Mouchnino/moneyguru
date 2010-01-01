/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGPieChart.h"
#import "MGPieChartView.h"

@implementation MGPieChart
- (id)initWithDocument:(MGDocument *)document pieChartClassName:(NSString *)className
{
    self = [super initWithPyClassName:className pyParent:[document py]];
    view = [[MGPieChartView alloc] init];
    return self;
}

- (void)dealloc
{
    [view release];
    [super dealloc];
}

- (PyChart *)py
{
    return (PyChart *)py;
}
@end