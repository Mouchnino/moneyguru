/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGTableView.h"
#import "MGSplitTable.h"
#import "PyTransactionPanel.h"

@class MGMainWindowController;

@interface MGTransactionInspector : MGPanel {
    NSTabView *tabView;
    NSTextField *dateField;
    NSTextField *descriptionField;
    NSTextField *payeeField;
    NSTextField *checknoField;
    NSTextField *notesField;
    MGTableView *splitTableView;
    NSButton *mctBalanceButton;
    
    MGSplitTable *splitTable;
}

@property (readwrite, retain) NSTabView *tabView;
@property (readwrite, retain) NSTextField *dateField;
@property (readwrite, retain) NSTextField *descriptionField;
@property (readwrite, retain) NSTextField *payeeField;
@property (readwrite, retain) NSTextField *checknoField;
@property (readwrite, retain) NSTextField *notesField;
@property (readwrite, retain) MGTableView *splitTableView;
@property (readwrite, retain) NSButton *mctBalanceButton;

- (id)initWithParent:(MGMainWindowController *)aParent;
- (PyTransactionPanel *)model;
/* Actions */
- (void)addSplit;
- (void)deleteSplit;
- (void)mctBalance;
@end
