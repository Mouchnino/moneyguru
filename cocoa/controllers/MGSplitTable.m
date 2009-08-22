/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSplitTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGUtils.h"

@implementation MGSplitTable

- (void)setTransactionPanel:(PyPanel *)aPanel;
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
    [[self py] add];
}

- (IBAction)deleteSplit:(id)sender
{
    [[self py] deleteSelectedRows];
}

@end