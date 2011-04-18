/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

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