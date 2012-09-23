/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSheetPrint.h"

/* I have no idea why (must be something like DPI and stuff), but the charts being drawn during
   print are drawn bigger than what they look like on screen. That's why we adjust chart size with
   this ratio below.
*/
#define VIEW_TO_PRINT_PROPORTIONS 0.7

@implementation MGSheetPrint
- (id)initWithPyParent:(PyGUIObject *)pyParent outlineView:(NSOutlineView *)aOutlineView 
    graphView:(NSView *)aGraphView pieView:(MGPieChartView *)aPieView
{
    self = [super initWithPyParent:pyParent tableView:aOutlineView];
    /* In the realm of "I have no idea why but it works":
       One other way to extract an image from drawing a view inside it is by using 
       [[NSBitmapImageRep alloc] initWithFocusedViewRect:[view bounds]];
       It works, but the result of it is an image drawn with a bad quality (which is strange
       because if you save the image to a file, the quality is alright). dataWithPDFInsideRect:
       needs to be used to have a good quality. So I have no idea why, but it works...
    */
    if (aGraphView != nil) {
        [aGraphView lockFocus];
        graphImage = [[NSImage alloc] initWithData:[aGraphView dataWithPDFInsideRect:[aGraphView bounds]]];
        [aGraphView unlockFocus];
    }
    else {
        graphImage = nil;
    }
    if (aPieView != nil) {
        [aPieView lockFocus];
        pieImage = [[NSImage alloc] initWithData:[aPieView dataWithPDFInsideRect:[aPieView bounds]]];
        [aPieView unlockFocus];
    }
    else {
        pieImage = nil;
    }
    
    return self;
}

-(void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [super setUpWithPrintInfo:pi];
    CGFloat columnsTotalWidth = [self columnsTotalWidth];
    CGFloat bottomY = lastRowYOnLastPage;
    piePage = -1;
    if (pieImage != nil) {
        pieRect.size = pieImage.size;
        pieRect.size.width *= VIEW_TO_PRINT_PROPORTIONS;
        pieRect.size.height *= VIEW_TO_PRINT_PROPORTIONS;
        if (pageWidth - columnsTotalWidth >= pieRect.size.width) {
            // We have enough space to fit the pie chart at the right of the sheet.
            pieRect.origin.x = columnsTotalWidth;
            pieRect.origin.y = headerHeight;
            piePage = 1;
        }
        else {
            pieRect.origin.x = 0;
            pieRect.origin.y = bottomY;
            bottomY = pieRect.origin.y + pieRect.size.height;
            if (bottomY > pageHeight) {
                pageCount++;
                pieRect.origin.y = headerHeight;
                bottomY = pieRect.origin.y + pieRect.size.height;
            }
            piePage = pageCount;
        }
    }
    graphPage = -1;
    if (graphImage != nil) {
        graphRect.size = graphImage.size;
        graphRect.size.width *= VIEW_TO_PRINT_PROPORTIONS;
        graphRect.size.height *= VIEW_TO_PRINT_PROPORTIONS;
        if (graphRect.size.width > pageWidth) {
            graphRect.size.width = pageWidth;
        }
        graphRect.origin.x = 0;
        graphRect.origin.y = pageHeight - graphRect.size.height;
        if (bottomY > graphRect.origin.y) {
            pageCount++;
            graphRect.origin.y = headerHeight;
        }
        graphPage = pageCount;
    }
}

- (void)dealloc
{
    [graphImage release];
    [pieImage release];
    [super dealloc];
}

- (void)drawRect:(NSRect)rect
{
    NSInteger pageNumber = [[NSPrintOperation currentOperation] currentPage];
    if (pageNumber == graphPage) {
        // If the simple drawRect: is used, our image is drawn flipped.
        [graphImage drawInRect:graphRect fromRect:NSZeroRect operation:NSCompositeSourceOver
            fraction:1.0 respectFlipped:YES hints:nil];
    }
    if (pageNumber == piePage) {
        [pieImage drawInRect:pieRect fromRect:NSZeroRect operation:NSCompositeSourceOver
            fraction:1.0 respectFlipped:YES hints:nil];
    }
    [super drawRect:rect];
}

@end