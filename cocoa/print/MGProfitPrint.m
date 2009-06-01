#import "MGProfitPrint.h"
#import "MGConst.h"

@implementation MGProfitPrint
- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"current",@"last",nil];
}

- (NSString *)pageTitle
{
    return [NSString stringWithFormat:@"Profit and loss from %@ to %@",[py startDate],[py endDate]];
}

-(void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    graphVisible = [ud boolForKey:ProfitGraphVisible];
    pieVisible = [ud boolForKey:IncomeExpensePieChartVisible];
    [super setUpWithPrintInfo:pi];
}
@end