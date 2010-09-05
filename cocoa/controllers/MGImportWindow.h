/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "PSMTabBarControl.h"
#import "HSGUIController.h"
#import "MGDocument.h"
#import "MGTableView.h"
#import "MGImportTable.h"
#import "MGImportTableOneSided.h"
#import "PyImportWindow.h"

@interface MGImportWindow : HSGUIController
{
    IBOutlet NSWindow *window;
    IBOutlet PSMTabBarControl *tabBar;
    IBOutlet NSTabView *tabView;
    IBOutlet NSView *mainView;
    IBOutlet NSPopUpButton *targetAccountsPopup;
    IBOutlet NSView *importTablePlaceholder;
    IBOutlet NSPopUpButton *switchDateFieldsPopup;
    IBOutlet NSButton *applySwapToAllCheckbox;
    IBOutlet NSButton *swapButton;
    IBOutlet MGTableView *importTableView;
    IBOutlet MGTableView *importTableOneSidedView;
    IBOutlet NSScrollView *importTableScrollView;
    IBOutlet NSScrollView *importTableOneSidedScrollView;
    
    MGImportTable *importTable;
    MGImportTableOneSided *importTableOneSided;
    id visibleTable;
    NSInteger tabToRemoveIndex;
}
- (id)initWithDocument:(MGDocument *)aDocument;

- (PyImportWindow *)py;
- (void)updateVisibleTable;
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