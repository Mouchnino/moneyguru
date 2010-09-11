/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGEntryPrint.h"
#import "MGConst.h"

#define GRAPH_HEIGHT_PROPORTION 0.4

@implementation MGEntryPrint
- (id)initWithPyParent:(id)pyParent tableView:(NSTableView *)aTableView graphView:(NSView *)aGraphView
{
    self = [super initWithPyParent:pyParent tableView:aTableView];
    graphView = [aGraphView copy];
    return self;
}

- (void)setUpWithPrintInfo:(NSPrintInfo *)pi
{
    [super setUpWithPrintInfo:pi];
    NSUserDefaults *ud = [NSUserDefaults standardUserDefaults];
    graphVisible = [ud boolForKey:AccountGraphVisible];
    if (graphVisible)
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

+ (NSString *)pyClassName
{
    return @"PyEntryPrint";
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
    BOOL shouldShowGraph = graphVisible && pageNumber == pageCount;
    [graphView setHidden:!shouldShowGraph];
    [super drawRect:rect];
}

@end