/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGTableView.h"
#import "PyExportPanel.h"
#import "MGExportAccountTable.h"

@class MGMainWindowController;

@interface MGExportPanel : MGPanel {
    IBOutlet NSMatrix *exportAllButtons;
    IBOutlet NSButton *exportButton;
    IBOutlet MGTableView *accountTableView;
    IBOutlet NSMatrix *exportFormatButtons;
    IBOutlet NSButton *currentDateRangeOnlyButton;
    
    MGExportAccountTable *accountTable;
}
- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyExportPanel *)py;
/* Actions */
- (IBAction)exportAllToggled:(id)sender;
- (IBAction)export:(id)sender;
@end
