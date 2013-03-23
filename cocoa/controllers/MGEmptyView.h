/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

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
    NSTableView *pluginTableView;
    
    HSSelectableList *pluginList;
}

@property (readwrite, retain) NSTableView *pluginTableView;

- (id)initWithPyRef:(PyObject *)aPyRef;
- (PyEmptyView *)model;

/* Actions */
- (void)selectNetWorthView;
- (void)selectProfitView;
- (void)selectTransactionView;
- (void)selectScheduleView;
- (void)selectBudgetView;
- (void)selectCashculatorView;
- (void)selectGeneralLedgerView;
- (void)selectDocPropsView;
- (void)selectPluginView;
@end