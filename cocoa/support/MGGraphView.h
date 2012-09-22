/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#import "MGChartView.h"

#define GRAPH_LINE_WIDTH 2.0
#define GRAPH_AXIS_OVERLAY_WIDTH 0.2
#define GRAPH_LABEL_FONT_SIZE 10.0
#define GRAPH_TITLE_FONT_SIZE 15.0

@interface MGGraphView : MGChartView 
{
    NSColor *axisColor;
    NSGradient *fillGradient;
    NSGradient *futureGradient;
}
@end

