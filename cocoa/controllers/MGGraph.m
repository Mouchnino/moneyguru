#import "MGGraph.h"

@implementation MGGraph
/* Override */
- (MGGraphView *)view
{
    return (MGGraphView *)view;
}

- (PyGraph *)py
{
    return (PyGraph *)py;
}

/* Python callbacks */
- (void)refresh
{
    [super refresh];
    [[self view] setMinX:[[self py] xMin]];
    [[self view] setMaxX:[[self py] xMax]];
    [[self view] setMinY:[[self py] yMin]];
    [[self view] setMaxY:[[self py] yMax]];
    [[self view] setXToday:[[self py] xToday]];
    [[self view] setXLabels:[[self py] xLabels]];
    [[self view] setYLabels:[[self py] yLabels]];
    [[self view] setXTickMarks:[[self py] xTickMarks]];
    [[self view] setYTickMarks:[[self py] yTickMarks]];
}
@end