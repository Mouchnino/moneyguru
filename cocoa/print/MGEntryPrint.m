/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGEntryPrint.h"
#import "MGConst.h"
#import "PyEntryPrint.h"

#define GRAPH_HEIGHT_PROPORTION 0.4

@implementation MGEntryPrint
- (id)initWithPyParent:(id)pyParent tableView:(NSTableView *)aTableView graphView:(NSView *)aGraphView
{
    self = [super initWithPyParent:pyParent tableView:aTableView];
    if (aGraphView != nil) {
        graphView = [aGraphView copy];
    }
    else {
        graphView = nil;
    }
    return self;
}

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [super setUpWithPrintInfo:pi];
    if (graphView != nil)
    {
        graphHeight = pageWidth * GRAPH_HEIGHT_PROPORTION;
        [graphView setHidden:YES];
        [self addSubview:graphView];
        graphY = lastRowYOnLastPage;
        if (graphY + graphHeight > pageHeight)
        {
            pageCount++;
            graphY = headerHeight;
        }
        [graphView setFrame:NSMakeRect(0, graphY, pageWidth, graphHeight)];
    }
}

- (void)dealloc
{
    [graphView release];
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
    if (graphView != nil) {
        BOOL shouldShowGraph = pageNumber == pageCount;
        [graphView setHidden:!shouldShowGraph];
    }
    [super drawRect:rect];
}

@end