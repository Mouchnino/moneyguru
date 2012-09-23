/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGEntryPrint.h"
#import "MGConst.h"
#import "PyEntryPrint.h"

#define VIEW_TO_PRINT_PROPORTIONS 0.7

@implementation MGEntryPrint
- (id)initWithPyParent:(PyGUIObject *)pyParent tableView:(NSTableView *)aTableView graphView:(NSView *)aGraphView
{
    self = [super initWithPyParent:pyParent tableView:aTableView];
    /* See MGSheetPrint for comments on chart drawing in a printing context.
    */
    if (aGraphView != nil) {
        [aGraphView lockFocus];
        graphImage = [[NSImage alloc] initWithData:[aGraphView dataWithPDFInsideRect:[aGraphView bounds]]];
        [aGraphView unlockFocus];
    }
    else {
        graphImage = nil;
    }
    return self;
}

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [super setUpWithPrintInfo:pi];
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
        if (lastRowYOnLastPage > graphRect.origin.y) {
            pageCount++;
            graphRect.origin.y = headerHeight;
        }
        graphPage = pageCount;
    }
}

- (void)dealloc
{
    [graphImage release];
    [super dealloc];
}

+ (Class)pyClass
{
    return [PyEntryPrint class];
}

- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"status",@"date",@"reconciliation_date",@"increase",
        @"decrease",@"balance",@"debit",@"credit",nil];
}

- (NSArray *)accountColumnNames
{
    return [NSArray arrayWithObjects:@"transfer",nil];
}

- (NSInteger)splitCountThreshold
{
    return 3;
}

- (void)drawRect:(NSRect)rect
{
    NSInteger pageNumber = [[NSPrintOperation currentOperation] currentPage];
    if (pageNumber == graphPage) {
        // If the simple drawRect: is used, our image is drawn flipped.
        [graphImage drawInRect:graphRect fromRect:NSZeroRect operation:NSCompositeSourceOver
            fraction:1.0 respectFlipped:YES hints:nil];
    }
    [super drawRect:rect];
}

@end