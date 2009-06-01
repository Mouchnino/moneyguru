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