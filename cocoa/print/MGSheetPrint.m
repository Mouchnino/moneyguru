/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSheetPrint.h"

#define GRAPH_HEIGHT_PROPORTION 0.4
#define PIE_GRAPH_MIN_WIDTH 170

@implementation MGSheetPrint
- (id)initWithPyParent:(PyGUIObject *)pyParent outlineView:(NSOutlineView *)aOutlineView 
    graphView:(NSView *)aGraphView pieViews:(MGDoubleView *)aPieViews
{
    self = [super initWithPyParent:pyParent tableView:aOutlineView];
    if (aGraphView != nil) {
        graphView = [aGraphView copy];
        [graphView setHidden:YES];
        [self addSubview:graphView];
    }
    else {
        graphView = nil;
    }
    if (aPieViews != nil) {
        pieViews = [[MGDoubleView alloc] init];
        [pieViews setHidden:YES];
        [self addSubview:pieViews];
        [pieViews setFirstView:[[[aPieViews firstView] copy] autorelease]];
        [pieViews setSecondView:[[[aPieViews secondView] copy] autorelease]];
    }
    else {
        pieViews = nil;
    }
    
    return self;
}

-(void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [super setUpWithPrintInfo:pi];
    CGFloat columnsTotalWidth = [self columnsTotalWidth];
    CGFloat bottomY = lastRowYOnLastPage;
    CGFloat pieX = columnsTotalWidth;
    CGFloat pieY = headerHeight;
    CGFloat pieWidth = pageWidth - columnsTotalWidth;
    CGFloat pieHeight = pageHeight - pieY;
    piePage = 1;
    BOOL isPieOnSide = pieWidth >= PIE_GRAPH_MIN_WIDTH;
    if ((pieViews != nil) && !isPieOnSide) {
        pieX = 0;
        pieY = bottomY;
        pieWidth = pageWidth;
        pieHeight = pieWidth * GRAPH_HEIGHT_PROPORTION;
        bottomY = pieY + pieHeight;
        if (bottomY > pageHeight) {
            pageCount++;
            pieY = headerHeight;
            bottomY = pieY + pieHeight;
        }
        piePage = pageCount;
    }
    CGFloat graphHeight = pageWidth * GRAPH_HEIGHT_PROPORTION;
    CGFloat graphY = pageHeight - graphHeight;
    if ((graphView != nil) && (bottomY > graphY)) {
        pageCount++;
        graphY = headerHeight;
    }
    graphPage = pageCount;

    
    // if there's only one page, the pies must stop when the graph starts
    if (isPieOnSide && (graphView != nil) && (pageCount == 1))
        pieHeight = graphY - pieY;
    if (pieViews != nil) {
        [pieViews setFrame:NSMakeRect(pieX, pieY, pieWidth, pieHeight)];
    }
    if (graphView != nil) {
        [graphView setFrame:NSMakeRect(0, graphY, pageWidth, graphHeight)];
    }
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
    if (graphView != nil) {
        BOOL showGraph = pageNumber == graphPage;
        [graphView setHidden:!showGraph];
    }
    if (pieViews != nil) {
        BOOL showPie = pageNumber == piePage;
        [pieViews setHidden:!showPie];
    }
    [super drawRect:rect];
}

@end