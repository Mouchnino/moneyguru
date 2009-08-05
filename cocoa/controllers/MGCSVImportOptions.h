/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGWindowController.h"
#import "MGDocument.h"
#import "PyCSVImportOptions.h"

@interface MGCSVImportOptions : MGWindowController
{
    IBOutlet NSTableView *csvDataTable;
    IBOutlet NSMenu *columnMenu;
    IBOutlet NSPopUpButton *layoutSelector;
    IBOutlet NSPopUpButton *targetSelector;
    
    int lastClickedColumnIndex;
}
- (id)initWithDocument:(MGDocument *)aDocument;
- (PyCSVImportOptions *)py;

/* Actions */
- (IBAction)cancel:(id)sender;
- (IBAction)continueImport:(id)sender;
- (IBAction)deleteSelectedLayout:(id)sender;
- (IBAction)newLayout:(id)sender;
- (IBAction)renameSelectedLayout:(id)sender;
- (IBAction)selectLayout:(id)sender;
- (IBAction)setColumnField:(id)sender;
- (IBAction)toggleLineExclusion:(id)sender;

/* Public */
- (BOOL)canDeleteLayout;
@end