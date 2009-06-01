#import "MGBalancePrint.h"
#import "MGConst.h"

@implementation MGBalancePrint
- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"start",@"end",nil];
}

- (NSString *)pageTitle
{
    return [NSString stringWithFormat:@"Net Worth at %@, starting from %@",[py endDate],[py startDate]];
}

-(void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    graphVisible = [ud boolForKey:NetWorthGraphVisible];
    pieVisible = [ud boolForKey:AssetLiabilityPieChartVisible];
    [super setUpWithPrintInfo:pi];
}
@end