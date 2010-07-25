/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSTableColumnManager.h"
#import "MGReport.h"
#import "PyBalanceSheet.h"

@interface MGBalanceSheet : MGReport
{
    HSTableColumnManager *columnsManager;
}
- (id)initWithPyParent:(id)aPyParent view:(HSOutlineView *)aOutlineView;
- (void)initializeColumns;
- (PyBalanceSheet *)py;
@end