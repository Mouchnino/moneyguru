/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGExportPanel.h"
#import "MGConst.h"
#import "MGMainWindowController.h"

// Synced with the core
#define MGExportFormatQIF 0
#define MGExportFormatCSV 1

@implementation MGExportPanel
- (id)initWithParent:(MGMainWindowController *)aParent
{
    self = [super initWithNibName:@"ExportPanel" py:[[aParent py] exportPanel] parent:aParent];
    accountTable = [[MGExportAccountTable alloc] initWithPy:[[self py] accountTable] view:accountTableView];
    return self;
}

- (void)dealloc
{
    [accountTable release];
    [super dealloc];
}

- (PyExportPanel *)py
{
    return (PyExportPanel *)py;
}

/* Override */
- (NSResponder *)firstField
{
    return accountTableView;
}

- (void)loadFields
{
    NSInteger exportAllRow = [[self py] exportAll] ? 0 : 1;
    [exportAllButtons selectCellAtRow:exportAllRow column:0];
    NSInteger exportFormat = [[self py] exportFormat];
    [exportFormatButtons selectCellAtRow:exportFormat column:0];
    NSInteger state = [[self py] currentDateRangeOnly] ? NSOnState : NSOffState;
    [currentDateRangeOnlyButton setState:state];
}

- (void)saveFields
{
    NSInteger exportFormat = [exportFormatButtons selectedRow] == 0 ? MGExportFormatQIF : MGExportFormatCSV;
    [[self py] setExportFormat:exportFormat];
    [[self py] setCurrentDateRangeOnly:[currentDateRangeOnlyButton state] == NSOnState];
}

/* Actions */
- (IBAction)exportAllToggled:(id)sender
{
    BOOL exportAll = [exportAllButtons selectedRow] == 0;
    [[self py] setExportAll:exportAll];
}

- (IBAction)export:(id)sender
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setTitle:TR(@"Export to file")];
    NSString *filename = [exportFormatButtons selectedRow] == 0 ? @"export.qif" : @"export.csv";
    if ([sp runModalForDirectory:nil file:filename] == NSOKButton) {
        NSString *filepath = [[sp URL] path];
        [[self py] setExportPath:filepath];
        [self save:sender];
    }
}

/* Python --> Cocoa */
- (void)setTableEnabled:(BOOL)enabled
{
    [accountTableView setEnabled:enabled];
}

- (void)setExportButtonEnabled:(BOOL)enabled
{
    [exportButton setEnabled:enabled];
}
@end