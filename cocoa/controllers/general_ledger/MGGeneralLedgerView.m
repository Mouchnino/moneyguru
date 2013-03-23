/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGeneralLedgerView.h"
#import "MGGeneralLedgerPrint.h"
#import "Utils.h"

@implementation MGGeneralLedgerView
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyGeneralLedgerView *m = [[PyGeneralLedgerView alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m release];
    tableView = [[MGGeneralLedgerTableView alloc] initWithFrame:NSMakeRect(0, 0, 100, 100)];
    [self setupTableView:tableView];
    mainResponder = tableView;
    self.view = [tableView wrapInScrollView];
    ledgerTable = [[MGGeneralLedgerTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
    [tableView release];
    return self;
}
        
- (void)dealloc
{
    [ledgerTable release];
    [super dealloc];
}

- (PyGeneralLedgerView *)model
{
    return (PyGeneralLedgerView *)model;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGGeneralLedgerPrint alloc] initWithPyParent:[self model] tableView:[ledgerTable tableView]] autorelease];
}

- (NSString *)tabIconName
{
    return @"gledger_16";
}

- (id)fieldEditorForObject:(id)asker
{
    return [ledgerTable fieldEditorForObject:asker];
}
@end