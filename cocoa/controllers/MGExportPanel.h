/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

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
    NSMatrix *exportAllButtons;
    NSButton *exportButton;
    MGTableView *accountTableView;
    NSMatrix *exportFormatButtons;
    NSButton *currentDateRangeOnlyButton;
    
    MGExportAccountTable *accountTable;
}

@property (readwrite, retain) NSMatrix *exportAllButtons;
@property (readwrite, retain) NSButton *exportButton;
@property (readwrite, retain) MGTableView *accountTableView;
@property (readwrite, retain) NSMatrix *exportFormatButtons;
@property (readwrite, retain) NSButton *currentDateRangeOnlyButton;

- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyExportPanel *)model;
/* Actions */
- (void)exportAllToggled;
- (void)export;
@end
