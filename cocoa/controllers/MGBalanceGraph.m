#import "MGBalanceGraph.h"
#import "PyBalanceGraph.h"

@implementation MGBalanceGraph
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName
{
    self = [super initWithPyClassName:aClassName pyParent:[aDocument py]];
    view = [[MGLineGraphView alloc] init];
    return self;
}

- (void)dealloc
{
    [view release];
    [super dealloc];
}

@end
