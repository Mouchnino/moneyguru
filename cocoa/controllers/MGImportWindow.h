/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PSMTabBarControl.h"
#import "PyDocument.h"
#import "MGTableView.h"
#import "MGImportTable.h"
#import "PyImportWindow.h"

@interface MGImportWindow : NSWindowController
{
    PSMTabBarControl *tabBar;
    NSTabView *tabView;
    NSView *mainView;
    NSPopUpButton *targetAccountsPopup;
    NSPopUpButton *switchDateFieldsPopup;
    NSButton *applySwapToAllCheckbox;
    NSButton *swapButton;
    MGTableView *importTableView;
    
    PyImportWindow *model;
    MGImportTable *importTable;
    NSInteger tabToRemoveIndex;
}

@property (readwrite, retain) PSMTabBarControl *tabBar;
@property (readwrite, retain) NSTabView *tabView;
@property (readwrite, retain) NSView *mainView;
@property (readwrite, retain) NSPopUpButton *targetAccountsPopup;
@property (readwrite, retain) NSPopUpButton *switchDateFieldsPopup;
@property (readwrite, retain) NSButton *applySwapToAllCheckbox;
@property (readwrite, retain) NSButton *swapButton;
@property (readwrite, retain) MGTableView *importTableView;

- (id)initWithDocument:(PyDocument *)aDocument;

/* Actions */
- (void)changeTargetAccount;
- (void)importSelectedPane;
- (void)selectSwapType;
- (void)switchDateFields;

/* Python callbacks */
- (void)close;
- (void)closeSelectedTab;
- (void)refreshTabs;
- (void)refreshTargetAccounts;
- (void)show;
- (void)updateSelectedPane;
@end