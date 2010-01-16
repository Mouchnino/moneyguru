/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGraphView.h"
#import "Utils.h"

@implementation MGGraphView

- (id)init
{
    self = [super init];
    NSColor *darkGreen = [NSColor colorWithDeviceRed:0.365 green:0.737 blue:0.337 alpha:1.0];
    NSColor *lightGreen = [NSColor colorWithDeviceRed:0.643 green:0.847 blue:0.62 alpha:1.0];
    fillGradient = [[NSGradient alloc] initWithStartingColor:darkGreen endingColor:lightGreen];
    NSColor *darkGray = [NSColor lightGrayColor];
    NSColor *lightGray = [darkGray blendedColorWithFraction:0.5 ofColor:[NSColor whiteColor]];
    futureGradient = [[NSGradient alloc] initWithStartingColor:darkGray endingColor:lightGray];
    return self;
}

- (void)dealloc
{
    [xLabels release];
    [yLabels release];
    [xTickMarks release];
    [yTickMarks release];
    [fillGradient release];
    [futureGradient release];
    [super dealloc];
}

- (id)copyWithZone:(NSZone *)zone
{
    MGGraphView *result = [super copyWithZone:zone];
    [result setMinX:minX];
    [result setMaxX:maxX];
    [result setMinY:minY];
    [result setMaxY:maxY];
    [result setXToday:xToday];
    [result setXLabels:xLabels];
    [result setYLabels:yLabels];
    [result setXTickMarks:xTickMarks];
    [result setYTickMarks:yTickMarks];
    return result;
}

- (void)drawGraph {}

- (void)drawRect:(NSRect)rect 
{
    [super drawRect:rect];
    // Setup some colors and fonts
    NSColor *axisColor = [NSColor darkGrayColor];
	NSFont *labelFont = [NSFont labelFontOfSize:GRAPH_LABEL_FONT_SIZE];
	NSDictionary *labelAttributes = [NSDictionary dictionaryWithObjectsAndKeys:labelFont, NSFontAttributeName, axisColor, NSForegroundColorAttributeName, nil];
    NSFont *titleFont = [NSFont boldSystemFontOfSize:GRAPH_TITLE_FONT_SIZE];
    NSDictionary *titleAttributes = [NSDictionary dictionaryWithObjectsAndKeys:titleFont, NSFontAttributeName, titleColor, NSForegroundColorAttributeName, nil];
	
	// Loop variables
	NSEnumerator *labelsEnumerator;
	NSDictionary *label;
	NSEnumerator *tickMarksEnumerator;
	NSNumber *tickMark;
	
	// Calculate the space taken by labels
	CGFloat labelsHeight = [labelFont pointSize];
	CGFloat yLabelsWidth = 0;
	labelsEnumerator = [yLabels objectEnumerator];
	while (label = [labelsEnumerator nextObject])
	{
		NSString *labelText = [label objectForKey:@"text"];
		NSSize labelSize = [labelText sizeWithAttributes:labelAttributes];
		if (labelSize.width > yLabelsWidth)	
        {
			yLabelsWidth = labelSize.width;
		}
	}
	
	// Calculate the graph dimensions
	CGFloat dataWidth = maxX - minX;
	CGFloat dataHeight = maxY - minY;
	NSSize viewSize = [self bounds].size;
	CGFloat graphWidth = viewSize.width - yLabelsWidth - GRAPH_PADDING * 2;
	CGFloat graphHeight = viewSize.height - labelsHeight - GRAPH_PADDING * 2; 
	xFactor = graphWidth / dataWidth;
	yFactor = graphHeight / dataHeight;
	CGFloat graphLeft = roundf((float)(minX * xFactor));
	CGFloat graphRight = roundf((float)(maxX * xFactor));
	CGFloat graphBottom = roundf((float)(minY * yFactor));
    if (graphBottom < 0)
    {
        // Leave some space at the bottom of the graph
        graphBottom -= 2 * GRAPH_LINE_WIDTH;
    }
	CGFloat graphTop = roundf((float)(maxY * yFactor));
    graphBounds = NSMakeRect(graphLeft, graphBottom, graphRight - graphLeft, graphTop - graphBottom);
	
	// Change the coordinates so that the drawing origin corresponds to the graph origin.
	NSAffineTransform *moveOrigin = [NSAffineTransform transform];
	[moveOrigin translateXBy:(ceilf((float)yLabelsWidth) + GRAPH_PADDING - graphLeft) yBy:(ceilf((float)labelsHeight) + GRAPH_PADDING - graphBottom)];
	[moveOrigin concat];

    // Draw the graph
	[self drawGraph];
    
	// Draw the X axis.
	[axisColor setStroke];
	NSBezierPath *xAxisPath = [NSBezierPath bezierPath];
    [xAxisPath setLineWidth:GRAPH_LINE_WIDTH];
	[xAxisPath moveToPoint:NSMakePoint(graphLeft - GRAPH_LINE_WIDTH / 2, graphBottom)];
	[xAxisPath lineToPoint:NSMakePoint(graphRight + GRAPH_LINE_WIDTH / 2, graphBottom)];
	[xAxisPath stroke];

	// Draw the Y axis.
	NSBezierPath *yAxisPath = [NSBezierPath bezierPath];
    [yAxisPath setLineWidth:GRAPH_LINE_WIDTH];
	[yAxisPath moveToPoint:NSMakePoint(graphLeft, graphBottom - GRAPH_LINE_WIDTH / 2)];
	[yAxisPath lineToPoint:NSMakePoint(graphLeft, graphTop + GRAPH_LINE_WIDTH / 2)];
	[yAxisPath stroke];
	
	// Draw the X tick marks
	NSBezierPath *xTickMarksPath = [NSBezierPath bezierPath];
    [xTickMarksPath setLineWidth:GRAPH_LINE_WIDTH];
	tickMarksEnumerator = [xTickMarks objectEnumerator];
	while (tickMark = [tickMarksEnumerator nextObject])
	{
		CGFloat tickMarkPos = roundf((float)(n2f(tickMark) * xFactor));
		[xTickMarksPath moveToPoint:NSMakePoint(tickMarkPos, graphBottom)];
		[xTickMarksPath lineToPoint:NSMakePoint(tickMarkPos, graphBottom - GRAPH_TICKMARKS_LENGTH)];
	}
	[xTickMarksPath stroke];
	
	// Draw the Y tick marks
	NSBezierPath *yTickMarksPath = [NSBezierPath bezierPath];
    [yTickMarksPath setLineWidth:GRAPH_LINE_WIDTH];
	tickMarksEnumerator = [yTickMarks objectEnumerator];
	while (tickMark = [tickMarksEnumerator nextObject])
	{
		CGFloat tickMarkPos = roundf((float)(n2f(tickMark) * yFactor));
		[yTickMarksPath moveToPoint:NSMakePoint(graphLeft, tickMarkPos)];
		[yTickMarksPath lineToPoint:NSMakePoint(graphLeft - GRAPH_TICKMARKS_LENGTH, tickMarkPos)];
	}
	[yTickMarksPath stroke];
	
	// Draw the X labels
	labelsEnumerator = [xLabels objectEnumerator];
	while (label = [labelsEnumerator nextObject])
	{
		NSString *labelText = [label objectForKey:@"text"];
		CGFloat labelPos = n2f([label objectForKey:@"pos"]) * xFactor;
		NSSize labelSize = [labelText sizeWithAttributes:labelAttributes];
		[labelText drawAtPoint:NSMakePoint(labelPos - labelSize.width / 2, graphBottom - labelsHeight - GRAPH_X_LABELS_PADDING) withAttributes:labelAttributes];
	}

	// Draw the Y labels
	labelsEnumerator = [yLabels objectEnumerator];
	while (label = [labelsEnumerator nextObject])
	{
		NSString *labelText = [label objectForKey:@"text"];
		CGFloat labelPos = n2f([label objectForKey:@"pos"]) * yFactor;
		NSSize labelSize = [labelText sizeWithAttributes:labelAttributes];
		[labelText drawAtPoint:NSMakePoint(graphLeft - GRAPH_Y_LABELS_PADDING - labelSize.width, labelPos - labelsHeight / 2) withAttributes:labelAttributes];
	}
	
    [moveOrigin invert];
    [moveOrigin concat];
    
    // Draw the title
    NSString *titleToDraw = [NSString stringWithFormat:@"%@ (%@)",title,currency];
    NSSize titleSize = [titleToDraw sizeWithAttributes:titleAttributes];
    CGFloat titlePos = viewSize.width / 2;
    CGFloat titleX = titlePos - titleSize.width / 2;
    CGFloat titleY = viewSize.height - titleSize.height - GRAPH_Y_TITLE_PADDING;
    [titleToDraw drawAtPoint:NSMakePoint(titleX, titleY) withAttributes:titleAttributes];    
}

- (void)setMinX:(CGFloat)aMinX
{
    minX = aMinX;
}

- (void)setMaxX:(CGFloat)aMaxX
{
    maxX = aMaxX;
}

- (void)setMinY:(CGFloat)aMinY
{
    minY = aMinY;
}

- (void)setMaxY:(CGFloat)aMaxY
{
    maxY = aMaxY;
}

- (void)setXToday:(CGFloat)aXToday
{
    xToday = aXToday;
}

- (void)setXLabels:(NSArray *)aXLabels
{
    [xLabels autorelease];
    xLabels = [aXLabels retain];
}

- (void)setYLabels:(NSArray *)aYLabels
{
    [yLabels autorelease];
    yLabels = [aYLabels retain];
}

- (void)setXTickMarks:(NSArray *)aXTickMarks
{
    [xTickMarks autorelease];
    xTickMarks = [aXTickMarks retain];
}

- (void)setYTickMarks:(NSArray *)aYTickMarks
{
    [yTickMarks autorelease];
    yTickMarks = [aYTickMarks retain];
}
@end
