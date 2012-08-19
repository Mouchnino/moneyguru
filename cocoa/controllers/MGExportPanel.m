/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGExportPanel.h"
#import "MGExportPanel_UI.h"
#import "MGMainWindowController.h"
#import "HSPyUtil.h"

// Synced with the core
#define MGExportFormatQIF 0
#define MGExportFormatCSV 1

@implementation MGExportPanel

@synthesize exportAllButtons;
@synthesize exportButton;
@synthesize accountTableView;
@synthesize exportFormatButtons;
@synthesize currentDateRangeOnlyButton;

- (id)initWithParent:(MGMainWindowController *)aParent
{
    PyExportPanel *m = [[PyExportPanel alloc] initWithModel:[[aParent model] exportPanel]];
    self = [super initWithModel:m parent:aParent];
    [m bindCallback:createCallback(@"ExportPanelView", self)];
    [m release];
    [self setWindow:createMGExportPanel_UI(self)];
    accountTable = [[MGExportAccountTable alloc] initWithPyRef:[[self model] accountTable] tableView:accountTableView];
    return self;
}

- (void)dealloc
{
    [accountTable release];
    [super dealloc];
}

- (PyExportPanel *)model
{
    return (PyExportPanel *)model;
}

/* Override */
- (NSResponder *)firstField
{
    return accountTableView;
}

- (void)loadFields
{
    NSInteger exportAllRow = [[self model] exportAll] ? 0 : 1;
    [exportAllButtons selectCellAtRow:exportAllRow column:0];
    NSInteger exportFormat = [[self model] exportFormat];
    [exportFormatButtons selectCellAtRow:exportFormat column:0];
    NSInteger state = [[self model] currentDateRangeOnly] ? NSOnState : NSOffState;
    [currentDateRangeOnlyButton setState:state];
}

- (void)saveFields
{
    NSInteger exportFormat = [exportFormatButtons selectedRow] == 0 ? MGExportFormatQIF : MGExportFormatCSV;
    [[self model] setExportFormat:exportFormat];
    [[self model] setCurrentDateRangeOnly:[currentDateRangeOnlyButton state] == NSOnState];
}

/* Actions */
- (void)exportAllToggled
{
    BOOL exportAll = [exportAllButtons selectedRow] == 0;
    [[self model] setExportAll:exportAll];
}

- (void)export
{
    NSSavePanel *sp = [NSSavePanel savePanel];
    [sp setCanCreateDirectories:YES];
    [sp setTitle:NSLocalizedString(@"Export to file", @"")];
    NSString *filename = [exportFormatButtons selectedRow] == 0 ? @"export.qif" : @"export.csv";
    [sp setNameFieldStringValue:filename];
    if ([sp runModal] == NSOKButton) {
        NSString *filepath = [[sp URL] path];
        [[self model] setExportPath:filepath];
        [self save:nil];
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