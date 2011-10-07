/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBalanceGraph.h"

@implementation MGBalanceGraph
- (id)initWithPyParent:(id)aPyParent pyClassName:(NSString *)aClassName
{
    MGLineGraphView *myview = [[MGLineGraphView alloc] init];
    self = [super initWithPyClassName:aClassName pyParent:aPyParent view:[myview autorelease]];
    return self;
}
@end
