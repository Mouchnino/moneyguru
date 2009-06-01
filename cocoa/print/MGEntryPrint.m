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

- (NSString *)pageTitle
{
    return [NSString stringWithFormat:@"Entries from %@ to %@",[py startDate],[py endDate]];
}

- (NSArray *)unresizableColumns
{
    return [NSArray arrayWithObjects:@"status",@"date",@"increase",@"decrease",@"balance",nil];
}

- (NSArray *)accountColumnNames
{
    return [NSArray arrayWithObjects:@"transfer",nil];
}

- (int)splitCountThreshold
{
    return 2;
}

- (void)drawRect:(NSRect)rect
{
    int pageNumber = [[NSPrintOperation currentOperation] currentPage];
    BOOL shouldShowGraph = graphVisible && pageNumber == pageCount;
    [graphView setHidden:!shouldShowGraph];
    [super drawRect:rect];
}

@end