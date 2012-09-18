/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGPieChart.h"
#import "MGPieChartView.h"
#import "Utils.h"

static NSColor* intToColor(NSInteger i)
{
    CGFloat r = ((i >> 16) & 255) / 255.0;
    CGFloat g = ((i >> 8) & 255) / 255.0;
    CGFloat b = (i & 255) / 255.0;
    return [NSColor colorWithDeviceRed:r green:g blue:b alpha:1.0];
}

@implementation MGPieChart
- (id)initWithPyRef:(PyObject *)aPyRef
{
    MGPieChartView *myview = [[MGPieChartView alloc] init];
    self = [super initWithPyRef:aPyRef];
    NSMutableArray *colors = [NSMutableArray array];
    for (NSNumber *nc in [[self model] colors]) {
        NSColor *c = intToColor(n2i(nc));
        [colors addObject:c];
    }
    [myview setColors:colors];
    [self setView:[myview autorelease]];
    return self;
}
@end