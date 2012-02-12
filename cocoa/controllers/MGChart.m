/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGChart.h"
#import "Utils.h"

@implementation MGChart
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyChart *m = [[PyChart alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"GUIObjectView", self)];
    [m release];
    return self;
}

/* Override */
- (MGChartView *)view
{
    return (MGChartView *)view;
}

- (void)setView:(MGChartView *)aView
{
    [super setView:aView];
    if (aView != nil) {
        [aView setModel:[self model]];
    }
}

- (PyChart *)model
{
    return (PyChart *)model;
}

/* Python callbacks */
- (void)refresh
{
    [[self view] setData:[[self model] data]];
    [[self view] setTitle:[[self model] title]];
    [[self view] setCurrency:[[self model] currency]];
    [[self view] setNeedsDisplay:YES];
}

@end
