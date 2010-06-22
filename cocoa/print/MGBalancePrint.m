/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGBalancePrint.h"
#import "MGConst.h"

@implementation MGBalancePrint
- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"start",@"end",nil];
}

- (NSString *)pageTitle
{
    return [NSString stringWithFormat:TR(@"NetWorthPrintTitle"),[py endDate],[py startDate]];
}

-(void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    graphVisible = [ud boolForKey:NetWorthGraphVisible];
    pieVisible = [ud boolForKey:AssetLiabilityPieChartVisible];
    [super setUpWithPrintInfo:pi];
}
@end