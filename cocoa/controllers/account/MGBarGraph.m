/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBarGraph.h"

@implementation MGBarGraph
- (id)initWithPyParent:(id)aPyParent pyClassName:(NSString *)aClassName
{
    MGBarGraphView *myview = [[MGBarGraphView alloc] init];
    self = [super initWithPyClassName:aClassName pyParent:aPyParent view:[myview autorelease]];
    return self;
}

- (id)initWithPy:(id)aPy
{
    MGBarGraphView *myview = [[MGBarGraphView alloc] init];
    self = [super initWithPy:aPy];
    [self setView:[myview autorelease]];
    return self;
}
@end
