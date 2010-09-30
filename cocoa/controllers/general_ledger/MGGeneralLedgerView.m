/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGGeneralLedgerView.h"
#import "MGGeneralLedgerPrint.h"
#import "Utils.h"

@implementation MGGeneralLedgerView
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyGeneralLedgerView" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"GeneralLedger" owner:self];
    ledgerTable = [[MGGeneralLedgerTable alloc] initWithPyParent:[self py] view:tableView];
    NSArray *children = [NSArray arrayWithObjects:[ledgerTable py], nil];
    [[self py] setChildren:children];
    return self;
}
        
- (void)dealloc
{
    [ledgerTable release];
    [super dealloc];
}

- (PyGeneralLedgerView *)py
{
    return (PyGeneralLedgerView *)py;
}

- (MGPrintView *)viewToPrint
{
    return [[[MGGeneralLedgerPrint alloc] initWithPyParent:[self py] tableView:[ledgerTable tableView]] autorelease];
}

- (id)fieldEditorForObject:(id)asker
{
    return [ledgerTable fieldEditorForObject:asker];
}
@end