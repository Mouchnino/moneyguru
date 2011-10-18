/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PSMTabBarControl.h"
#import "HSWindowController.h"
#import "MGDocument.h"
#import "MGTableView.h"
#import "MGImportTable.h"
#import "PyImportWindow.h"

@interface MGImportWindow : HSWindowController
{
    IBOutlet PSMTabBarControl *tabBar;
    IBOutlet NSTabView *tabView;
    IBOutlet NSView *mainView;
    IBOutlet NSPopUpButton *targetAccountsPopup;
    IBOutlet NSPopUpButton *switchDateFieldsPopup;
    IBOutlet NSButton *applySwapToAllCheckbox;
    IBOutlet NSButton *swapButton;
    IBOutlet MGTableView *importTableView;
    
    MGImportTable *importTable;
    NSInteger tabToRemoveIndex;
}
- (id)initWithDocument:(MGDocument *)aDocument;

- (PyImportWindow *)py;
/* Actions */
- (IBAction)changeTargetAccount:(id)sender;
- (IBAction)importSelectedPane:(id)sender;
- (IBAction)selectSwapType:(id)sender;
- (IBAction)switchDateFields:(id)sender;

/* Python callbacks */
- (void)close;
- (void)closeSelectedTab;
- (void)refreshTabs;
- (void)refreshTargetAccounts;
- (void)show;
- (void)updateSelectedPane;
@end