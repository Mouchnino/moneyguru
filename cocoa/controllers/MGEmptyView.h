/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyEmptyView.h"
#import "MGBaseView.h"
#import "HSSelectableList.h"

@interface MGEmptyView : MGBaseView
{
    IBOutlet NSTableView *pluginTableView;
    
    HSSelectableList *pluginList;
}
- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyEmptyView *)model;

/* Actions */
- (IBAction)selectNetWorthView:(id)sender;
- (IBAction)selectProfitView:(id)sender;
- (IBAction)selectTransactionView:(id)sender;
- (IBAction)selectScheduleView:(id)sender;
- (IBAction)selectBudgetView:(id)sender;
- (IBAction)selectCashculatorView:(id)sender;
- (IBAction)selectGeneralLedgerView:(id)sender;
- (IBAction)selectDocPropsView:(id)sender;
- (IBAction)selectPluginView:(id)sender;
@end