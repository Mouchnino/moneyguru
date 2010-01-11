/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGCSVImportOptions.h"
#import "MGCSVLayoutNameDialog.h"
#import "Utils.h"

@implementation MGCSVImportOptions
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithNibName:@"CSVImportOptions" pyClassName:@"PyCSVImportOptions" pyParent:[aDocument py]];
    [self window];
    return self;
}

- (void)dealloc
{
    [super dealloc];
}

- (PyCSVImportOptions *)py
{
    return (PyCSVImportOptions *)py;
}

/* Actions */

- (IBAction)cancel:(id)sender
{
    [[self window] orderOut:self];
}

- (IBAction)continueImport:(id)sender
{
    [[self py] continueImport];
}

- (IBAction)deleteSelectedLayout:(id)sender
{
    [[self py] deleteSelectedLayout];
}

- (IBAction)newLayout:(id)sender
{
    NSString *layoutName = [MGCSVLayoutNameDialog askForLayoutName];
    if (layoutName != nil)
        [[self py] newLayout:layoutName];
    else
        [layoutSelector selectItemWithTitle:[[self py] selectedLayoutName]];
}

- (IBAction)renameSelectedLayout:(id)sender
{
    NSString *layoutName = [MGCSVLayoutNameDialog askForLayoutNameBasedOnOldName:[[self py] selectedLayoutName]];
    if (layoutName != nil)
        [[self py] renameSelectedLayout:layoutName];
    else
        [layoutSelector selectItemWithTitle:[[self py] selectedLayoutName]];
}

- (IBAction)rescan:(id)sender
{
    [[self py] setFieldSeparator:[delimiterTextField stringValue]];
    [[self py] rescan];
}

- (IBAction)selectLayout:(id)sender
{
    NSMenuItem *item = sender;
    if ([layoutSelector indexOfItem:item] == 0) // Default
        [[self py] selectLayout:nil];
    else
        [[self py] selectLayout:[item title]];
}

- (IBAction)selectTarget:(id)sender
{
    [[self py] setSelectedTargetIndex:[targetSelector indexOfSelectedItem]];
}

- (IBAction)setColumnField:(id)sender
{
    [[self py] setColumn:lastClickedColumnIndex-1 fieldForTag:[sender tag]];
}

- (IBAction)toggleLineExclusion:(id)sender
{
    [[self py] toggleLineExclusion:[csvDataTable selectedRow]];
}

/* Public */

- (BOOL)canDeleteLayout
{
    return [layoutSelector indexOfSelectedItem] > 0;
}

/* Datasource */

- (int)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [[self py] numberOfLines];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)tableColumn row:(int)rowIndex
{
    id identifier = [tableColumn identifier];
    if ([@"import" isEqualTo:identifier])
        return i2n([[self py] lineIsImported:rowIndex]);
    else
        return [[self py] valueForRow:rowIndex column:n2i(identifier)];
}

/* Delegate */

- (void)tableView:(NSTableView *)tableView didClickTableColumn:(NSTableColumn *)tableColumn
{
    lastClickedColumnIndex = [[tableView tableColumns] indexOfObject:tableColumn];
    if (lastClickedColumnIndex > 0)
        [NSMenu popUpContextMenu:columnMenu withEvent:[NSApp currentEvent] forView:tableView];
}

/* Python callbacks */

- (void)refreshColumnsName
{
    for (int i=1; i<[[csvDataTable tableColumns] count]; i++)
    {
        NSString *columnName = [[self py] columnNameAtIndex:i-1];
        NSTableColumn *column = [[csvDataTable tableColumns] objectAtIndex:i];
        [[column headerCell] setStringValue:columnName];
    }
    // If not done, the header doesn't update unless a scrolling occurs.
    [[csvDataTable headerView] setNeedsDisplay:YES];
}

- (void)refreshColumns
{
    int columnCount = [[self py] numberOfColumns] + 1; // we have to count the "import" column
    while ([[csvDataTable tableColumns] count] > columnCount)
        [csvDataTable removeTableColumn:[[csvDataTable tableColumns] objectAtIndex:columnCount]];
    while ([[csvDataTable tableColumns] count] < columnCount)
    {
        int colId = [[csvDataTable tableColumns] count] - 1;
        NSTableColumn *column = [[[NSTableColumn alloc] initWithIdentifier:i2n(colId)] autorelease];
        [column setWidth:80];
        NSFont *font = [[column dataCell] font];
        font = [[NSFontManager sharedFontManager] convertFont:font toSize:11];
        [[column dataCell] setFont:font];
        [csvDataTable addTableColumn:column];
        [csvDataTable setIndicatorImage:[NSImage imageNamed:@"popup_arrows"] inTableColumn:column];
    }
    [self refreshColumnsName];
}

- (void)refreshLayoutMenu
{
    // First, remove all menu items until the first separator item
    while (![[layoutSelector itemAtIndex:0] isSeparatorItem])
        [layoutSelector removeItemAtIndex:0];
    NSArray *layoutNames = [[self py] layoutNames];
    for (int i=0; i<[layoutNames count]; i++)
    {
        NSString *title = [layoutNames objectAtIndex:i];
        NSMenuItem *item = [[[NSMenuItem alloc] initWithTitle:title action:@selector(selectLayout:) keyEquivalent:@""] autorelease];
        [item setTarget:self];
        [[layoutSelector menu] insertItem:item atIndex:i];
    }   
    [layoutSelector selectItemWithTitle:[[self py] selectedLayoutName]];
}

- (void)refreshLines
{
    [csvDataTable reloadData];
    [delimiterTextField setStringValue:[[self py] fieldSeparator]];
}

- (void)refreshTargets
{
    [targetSelector removeAllItems];
    [targetSelector addItemsWithTitles:[[self py] targetAccountNames]];
    [targetSelector selectItemAtIndex:[[self py] selectedTargetIndex]];
}

- (void)show
{
    [[self window] makeKeyAndOrderFront:self];
}

- (void)hide
{
    [[self window] orderOut:self];
}
@end