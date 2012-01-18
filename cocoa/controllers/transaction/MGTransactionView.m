/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

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
    transactionTable = [[MGTransactionTable alloc] initWithPy:[[self py] table] view:tableView];
    filterBar = [[MGFilterBar alloc] initWithPy:[[self py] filterBar] view:filterBarView forEntryTable:NO];
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