/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChart.h"

@implementation MGChart
/* Override */
- (MGChartView *)view
{
    return (MGChartView *)view;
}

- (PyChart *)py
{
    return (PyChart *)py;
}

/* Python callbacks */
- (void)refresh
{
    [[self view] setData:[[self py] data]];
    [[self view] setTitle:[[self py] title]];
    [[self view] setCurrency:[[self py] currency]];
    [[self view] setNeedsDisplay:YES];
}

@end
