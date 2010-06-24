/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#import "MGChartView.h"

#define GRAPH_PADDING 20.0
#define GRAPH_LINE_WIDTH 2.0
#define GRAPH_LABEL_FONT_SIZE 10.0
#define GRAPH_TITLE_FONT_SIZE 15.0
#define GRAPH_TICKMARKS_LENGTH 5.0
#define GRAPH_X_LABELS_PADDING 4.0
#define GRAPH_Y_LABELS_PADDING 7.0
#define GRAPH_Y_TITLE_PADDING 7.0

@interface MGGraphView : MGChartView 
{
    CGFloat minX;
    CGFloat maxX;
    CGFloat minY;
    CGFloat maxY;
    CGFloat xToday;
    NSArray *xLabels;
    NSArray *yLabels;
    NSArray *xTickMarks;
    NSArray *yTickMarks;
    CGFloat xFactor;
    CGFloat yFactor;
    NSRect graphBounds;
    NSGradient *fillGradient;
    NSGradient *futureGradient;
}
- (void)setMinX:(CGFloat)aMinX;
- (void)setMaxX:(CGFloat)aMaxX;
- (void)setMinY:(CGFloat)aMinY;
- (void)setMaxY:(CGFloat)aMaxY;
- (void)setXToday:(CGFloat)aXToday;
- (void)setXLabels:(NSArray *)aXLabels;
- (void)setYLabels:(NSArray *)aYLabels;
- (void)setXTickMarks:(NSArray *)aXTickMarks;
- (void)setYTickMarks:(NSArray *)aYTickMarks;
@end

