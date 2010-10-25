/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGExportPanel.h"
#import "MGConst.h"

@implementation MGExportPanel
- (id)initWithParent:(HSWindowController *)aParent
{
    self = [super initWithNibName:@"ExportPanel" pyClassName:@"PyExportPanel" parent:aParent];
    accountTable = [[MGExportAccountTable alloc] initWithPyParent:[self py] view:accountTableView];
    [accountTable connect];
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
    [sp setTitle:TR(@"ExportToQIFMsg")];
    if ([sp runModalForDirectory:nil file:@"export.qif"] == NSOKButton) {
        NSString *filename = [[sp URL] path];
        [[self py] setExportPath:filename];
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