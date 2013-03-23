/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyGeneralLedgerView.h"
#import "MGBaseView.h"
#import "MGGeneralLedgerTable.h"
#import "MGGeneralLedgerTableView.h"

@interface MGGeneralLedgerView : MGBaseView
{
    MGGeneralLedgerTableView *tableView;
    MGGeneralLedgerTable *ledgerTable;
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyGeneralLedgerView *)model;
@end