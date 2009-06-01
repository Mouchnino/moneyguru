#import "MGSplitTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGUtils.h"

@implementation MGSplitTable

- (void)setTransactionPanel:(PyTransactionPanel *)aPanel;
{
    if (py != nil)
    {
        [py free];
        [py release];
        py = nil;
    }
    if (aPanel != nil)
    {
        Class pyClass = [MGUtils classNamed:@"PySplitTable"];
        py = [[pyClass alloc] initWithCocoa:self pyParent:aPanel];
        [py connect];
    }
}

- (void)dealloc
{
    [self setTransactionPanel:nil];
    [super dealloc];
}

/* Actions */

- (IBAction)addSplit:(id)sender
{
    [self add];
}

- (IBAction)deleteSplit:(id)sender
{
    [self deleteSelected];
}

@end