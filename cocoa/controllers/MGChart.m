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
