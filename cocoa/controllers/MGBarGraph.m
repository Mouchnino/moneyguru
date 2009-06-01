#import "MGBarGraph.h"

@implementation MGBarGraph
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName
{
    self = [super initWithPyClassName:aClassName pyParent:[aDocument py]];
    view = [[MGBarGraphView alloc] init];
    return self;
}

- (void)dealloc
{
    [view release];
    [super dealloc];
}

@end
