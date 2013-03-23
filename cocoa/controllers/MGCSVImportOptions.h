/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "PyDocument.h"
#import "PyCSVImportOptions.h"

@interface MGCSVImportOptions : NSWindowController <NSTableViewDelegate, NSTableViewDataSource>
{
    NSTableView *csvDataTable;
    NSMenu *columnMenu;
    NSPopUpButton *layoutSelector;
    NSPopUpButton *encodingSelector;
    NSPopUpButton *targetSelector;
    NSTextField *delimiterTextField;
    
    NSInteger lastClickedColumnIndex;
    PyCSVImportOptions *model;
}

@property (readwrite, retain) NSTableView *csvDataTable;
@property (readwrite, retain) NSMenu *columnMenu;
@property (readwrite, retain) NSPopUpButton *layoutSelector;
@property (readwrite, retain) NSPopUpButton *encodingSelector;
@property (readwrite, retain) NSPopUpButton *targetSelector;
@property (readwrite, retain) NSTextField *delimiterTextField;

- (id)initWithDocument:(PyDocument *)aDocument;

/* Actions */
- (void)cancel;
- (void)continueImport;
- (void)deleteSelectedLayout;
- (void)newLayout;
- (void)renameSelectedLayout;
- (void)rescan;
- (void)selectLayout:(id)sender;
- (void)selectTarget;
- (void)setColumnField:(id)sender;
- (void)toggleLineExclusion;

/* Public */
- (BOOL)canDeleteLayout;
@end