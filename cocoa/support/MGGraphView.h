#import <Cocoa/Cocoa.h>
#import <ApplicationServices/ApplicationServices.h>
#import "MGChartView.h"
#import "MGGradient.h"

#define GRAPH_PADDING 20.0
#define GRAPH_LINE_WIDTH 2.0
#define GRAPH_LABEL_FONT_SIZE 10.0
#define GRAPH_TITLE_FONT_SIZE 22.0
#define GRAPH_TICKMARKS_LENGTH 5.0
#define GRAPH_X_LABELS_PADDING 4.0
#define GRAPH_Y_LABELS_PADDING 7.0
#define GRAPH_Y_TITLE_PADDING 7.0

@interface MGGraphView : MGChartView 
{
    float minX;
    float maxX;
    float minY;
    float maxY;
    float xToday;
    NSArray *xLabels;
    NSArray *yLabels;
    NSArray *xTickMarks;
    NSArray *yTickMarks;
    float xFactor;
    float yFactor;
    NSRect graphBounds;
    MGGradient *fillGradient;
    MGGradient *futureGradient;
}
- (void)setMinX:(float)aMinX;
- (void)setMaxX:(float)aMaxX;
- (void)setMinY:(float)aMinY;
- (void)setMaxY:(float)aMaxY;
- (void)setXToday:(float)aXToday;
- (void)setXLabels:(NSArray *)aXLabels;
- (void)setYLabels:(NSArray *)aYLabels;
- (void)setXTickMarks:(NSArray *)aXTickMarks;
- (void)setYTickMarks:(NSArray *)aYTickMarks;
@end

