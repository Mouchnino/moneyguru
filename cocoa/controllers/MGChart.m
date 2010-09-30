/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChart.h"

@implementation MGChart
/* Override */
- (MGChartView *)view
{
    return view;
}

- (PyChart *)py
{
    return (PyChart *)py;
}

/* Python callbacks */
- (void)refresh
{
    [view setData:[[self py] data]];
    [view setTitle:[[self py] title]];
    [view setCurrency:[[self py] currency]];
    [view setNeedsDisplay:YES];
}

@end
