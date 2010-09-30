/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSheetPrint.h"

#define GRAPH_HEIGHT_PROPORTION 0.4
#define PIE_GRAPH_MIN_WIDTH 170

@implementation MGSheetPrint
- (id)initWithPyParent:(id)pyParent outlineView:(NSOutlineView *)aOutlineView 
    graphView:(NSView *)aGraphView pieViews:(MGDoubleView *)aPieViews
{
    self = [super initWithPyParent:pyParent tableView:aOutlineView];
    graphView = [aGraphView copy];
    [graphView setHidden:YES];
    [self addSubview:graphView];
    pieViews = [[MGDoubleView alloc] init];
    [pieViews setHidden:YES];
    [self addSubview:pieViews];
    [pieViews setFirstView:[[[aPieViews firstView] copy] autorelease]];
    [pieViews setSecondView:[[[aPieViews secondView] copy] autorelease]];
    
    return self;
}

-(void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    // subclasses must set graphVisible and pieVisible before calling [super setUpWithPrintInfo:pi]
    [super setUpWithPrintInfo:pi];
    CGFloat columnsTotalWidth = [self columnsTotalWidth];
    CGFloat bottomY = lastRowYOnLastPage;
    CGFloat pieX = columnsTotalWidth;
    CGFloat pieY = headerHeight;
    CGFloat pieWidth = pageWidth - columnsTotalWidth;
    CGFloat pieHeight = pageHeight - pieY;
    piePage = 1;
    BOOL isPieOnSide = pieWidth >= PIE_GRAPH_MIN_WIDTH;
    if (pieVisible && !isPieOnSide)
    {
        pieX = 0;
        pieY = bottomY;
        pieWidth = pageWidth;
        pieHeight = pieWidth * GRAPH_HEIGHT_PROPORTION;
        bottomY = pieY + pieHeight;
        if (bottomY > pageHeight)
        {
            pageCount++;
            pieY = headerHeight;
            bottomY = pieY + pieHeight;
        }
        piePage = pageCount;
    }
    CGFloat graphHeight = pageWidth * GRAPH_HEIGHT_PROPORTION;
    CGFloat graphY = pageHeight - graphHeight;
    if (graphVisible && (bottomY > graphY))
    {
        pageCount++;
        graphY = headerHeight;
    }
    graphPage = pageCount;

    
    // if there's only one page, the pies must stop when the graph starts
    if (isPieOnSide && graphVisible && (pageCount == 1))
        pieHeight = graphY - pieY;
    [pieViews setFrame:NSMakeRect(pieX, pieY, pieWidth, pieHeight)];
    [graphView setFrame:NSMakeRect(0, graphY, pageWidth, graphHeight)];
}

- (void)dealloc
{
    [graphView release];
    [pieViews release];
    [super dealloc];
}

- (void)drawRect:(NSRect)rect
{
    NSInteger pageNumber = [[NSPrintOperation currentOperation] currentPage];
    BOOL showGraph = graphVisible && pageNumber == graphPage;
    [graphView setHidden:!showGraph];
    BOOL showPie = pieVisible && pageNumber == piePage;
    [pieViews setHidden:!showPie];
    [super drawRect:rect];
}

@end