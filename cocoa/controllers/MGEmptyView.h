/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyEmptyView.h"
#import "MGBaseView.h"

@interface MGEmptyView : MGBaseView
{
}
- (id)initWithPyParent:(id)aPyParent;
- (PyEmptyView *)py;

/* Actions */
- (IBAction)selectNetWorthView:(id)sender;
- (IBAction)selectProfitView:(id)sender;
- (IBAction)selectTransactionView:(id)sender;
- (IBAction)selectScheduleView:(id)sender;
- (IBAction)selectBudgetView:(id)sender;
- (IBAction)selectCashculatorView:(id)sender;
- (IBAction)selectGeneralLedgerView:(id)sender;
@end