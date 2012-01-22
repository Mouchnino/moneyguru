/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGraph.h"
#import "Utils.h"

@implementation MGGraph
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyGraph *m = [[PyGraph alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"GUIObjectView", self)];
    [m release];
    return self;
}

/* Override */
- (MGGraphView *)view
{
    return (MGGraphView *)view;
}

- (PyGraph *)model
{
    return (PyGraph *)model;
}

/* Python callbacks */
- (void)refresh
{
    [super refresh];
    [[self view] setMinX:[[self model] xMin]];
    [[self view] setMaxX:[[self model] xMax]];
    [[self view] setMinY:[[self model] yMin]];
    [[self view] setMaxY:[[self model] yMax]];
    [[self view] setXToday:[[self model] xToday]];
    [[self view] setXLabels:[[self model] xLabels]];
    [[self view] setYLabels:[[self model] yLabels]];
    [[self view] setXTickMarks:[[self model] xTickMarks]];
    [[self view] setYTickMarks:[[self model] yTickMarks]];
}
@end