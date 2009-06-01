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