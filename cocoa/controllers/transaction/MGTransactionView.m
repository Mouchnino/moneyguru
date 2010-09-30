/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGTransactionView.h"
#import "MGTransactionPrint.h"
#import "Utils.h"

@implementation MGTransactionView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyTransactionView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"TransactionTable" owner:self];
    transactionTable = [[MGTransactionTable alloc] initWithPyParent:[self py] view:tableView];
    filterBar = [[MGFilterBar alloc] initWithPyParent:[self py] view:filterBarView forEntryTable:NO];
    NSArray *children = [NSArray arrayWithObjects:[transactionTable py], [filterBar py], nil];
    [[self py] setChildren:children];
    return self;
}
        
- (void)dealloc
{
    [transactionTable release];
    [filterBar release];
    [super dealloc];
}

- (PyTransactionView *)py
{
    return (PyTransactionView *)py;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGTransactionPrint alloc] initWithPyParent:[self py] 
        tableView:[transactionTable tableView]] autorelease];
}

- (id)fieldEditorForObject:(id)asker
{
    return [transactionTable fieldEditorForObject:asker];
}
@end