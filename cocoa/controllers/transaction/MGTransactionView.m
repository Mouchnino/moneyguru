/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTransactionView.h"

@implementation MGTransactionView
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super init];
    [NSBundle loadNibNamed:@"TransactionTable" owner:self];
    transactionTable = [[MGTransactionTable alloc] initWithDocument:aDocument view:tableView];
    filterBar = [[MGFilterBar alloc] initWithDocument:aDocument view:filterBarView forEntryTable:NO];
    return self;
}
        
- (void)dealloc
{
    [transactionTable release];
    [filterBar release];
    [super dealloc];
}

- (NSView *)view
{
    return wholeView;
}

- (MGPrintView *)viewToPrint
{
    return [transactionTable viewToPrint];
}

- (void)connect
{
    [transactionTable connect];
    [filterBar connect];
}

- (void)disconnect
{
    [transactionTable disconnect];
    [filterBar disconnect];
}

- (MGTransactionTable *)transactionTable
{
    return transactionTable;
}
@end