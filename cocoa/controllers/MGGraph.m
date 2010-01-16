/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
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
    [[self view] setMinX:(CGFloat)[[self py] xMin]];
    [[self view] setMaxX:(CGFloat)[[self py] xMax]];
    [[self view] setMinY:(CGFloat)[[self py] yMin]];
    [[self view] setMaxY:(CGFloat)[[self py] yMax]];
    [[self view] setXToday:(CGFloat)[[self py] xToday]];
    [[self view] setXLabels:[[self py] xLabels]];
    [[self view] setYLabels:[[self py] yLabels]];
    [[self view] setXTickMarks:[[self py] xTickMarks]];
    [[self view] setYTickMarks:[[self py] yTickMarks]];
}
@end