/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

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
    [NSBundle loadNibNamed:@"GeneralLedger" owner:self];
    ledgerTable = [[MGGeneralLedgerTable alloc] initWithPyRef:[[self model] table] tableView:tableView];
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

- (id)fieldEditorForObject:(id)asker
{
    return [ledgerTable fieldEditorForObject:asker];
}
@end