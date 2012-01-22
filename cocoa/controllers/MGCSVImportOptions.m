/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGCSVImportOptions.h"
#import "MGCSVLayoutNameDialog.h"
#import "Utils.h"

@implementation MGCSVImportOptions
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithWindowNibName:@"CSVImportOptions"];
    [self window];
    model = [[PyCSVImportOptions alloc] initWithDocument:[[aDocument model] pyRef]];
    [model bindCallback:createCallback(@"CSVImportOptionsView", self)];
    [encodingSelector addItemsWithTitles:[model supportedEncodings]];
    [model connect];
    return self;
}

- (void)dealloc
{
    [model release];
    [super dealloc];
}

/* Actions */

- (IBAction)cancel:(id)sender
{
    [[self window] orderOut:self];
}

- (IBAction)continueImport:(id)sender
{
    [model continueImport];
}

- (IBAction)deleteSelectedLayout:(id)sender
{
    [model deleteSelectedLayout];
}

- (IBAction)newLayout:(id)sender
{
    NSString *layoutName = [MGCSVLayoutNameDialog askForLayoutName];
    if (layoutName != nil)
        [model newLayout:layoutName];
    else
        [layoutSelector selectItemWithTitle:[model selectedLayoutName]];
}

- (IBAction)renameSelectedLayout:(id)sender
{
    NSString *layoutName = [MGCSVLayoutNameDialog askForLayoutNameBasedOnOldName:[model selectedLayoutName]];
    if (layoutName != nil)
        [model renameSelectedLayout:layoutName];
    else
        [layoutSelector selectItemWithTitle:[model selectedLayoutName]];
}

- (IBAction)rescan:(id)sender
{
    [model setFieldSeparator:[delimiterTextField stringValue]];
    [model setEncodingIndex:[encodingSelector indexOfSelectedItem]];
    [model rescan];
}

- (IBAction)selectLayout:(id)sender
{
    NSMenuItem *item = sender;
    if ([layoutSelector indexOfItem:item] == 0) // Default
        [model selectLayout:nil];
    else
        [model selectLayout:[item title]];
}

- (IBAction)selectTarget:(id)sender
{
    [model setSelectedTargetIndex:[targetSelector indexOfSelectedItem]];
}

- (IBAction)setColumnField:(id)sender
{
    [model setColumn:lastClickedColumnIndex-1 fieldForTag:[sender tag]];
}

- (IBAction)toggleLineExclusion:(id)sender
{
    [model toggleLineExclusion:[csvDataTable selectedRow]];
}

/* Public */

- (BOOL)canDeleteLayout
{
    return [layoutSelector indexOfSelectedItem] > 0;
}

/* Datasource */

- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [model numberOfLines];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)tableColumn row:(NSInteger)rowIndex
{
    id identifier = [tableColumn identifier];
    if ([@"import" isEqualTo:identifier])
        return i2n([model lineIsImported:rowIndex]);
    else
        return [model valueForRow:rowIndex column:n2i(identifier)];
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
        NSString *columnName = [model columnNameAtIndex:i-1];
        NSTableColumn *column = [[csvDataTable tableColumns] objectAtIndex:i];
        [[column headerCell] setStringValue:columnName];
    }
    // If not done, the header doesn't update unless a scrolling occurs.
    [[csvDataTable headerView] setNeedsDisplay:YES];
}

- (void)refreshColumns
{
    NSInteger columnCount = [model numberOfColumns] + 1; // we have to count the "import" column
    while ([[csvDataTable tableColumns] count] > columnCount)
        [csvDataTable removeTableColumn:[[csvDataTable tableColumns] objectAtIndex:columnCount]];
    while ([[csvDataTable tableColumns] count] < columnCount)
    {
        NSInteger colId = [[csvDataTable tableColumns] count] - 1;
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
    NSArray *layoutNames = [model layoutNames];
    for (int i=0; i<[layoutNames count]; i++)
    {
        NSString *title = [layoutNames objectAtIndex:i];
        NSMenuItem *item = [[[NSMenuItem alloc] initWithTitle:title action:@selector(selectLayout:) keyEquivalent:@""] autorelease];
        [item setTarget:self];
        [[layoutSelector menu] insertItem:item atIndex:i];
    }   
    [layoutSelector selectItemWithTitle:[model selectedLayoutName]];
}

- (void)refreshLines
{
    [csvDataTable reloadData];
    [delimiterTextField setStringValue:[model fieldSeparator]];
}

- (void)refreshTargets
{
    [targetSelector removeAllItems];
    [targetSelector addItemsWithTitles:[model targetAccountNames]];
    [targetSelector selectItemAtIndex:[model selectedTargetIndex]];
}

- (void)show
{
    [[self window] makeKeyAndOrderFront:self];
}

- (void)hide
{
    [[self window] orderOut:self];
}

- (void)showMessage:(NSString *)msg
{
    NSAlert *a = [NSAlert alertWithMessageText:msg defaultButton:nil alternateButton:nil 
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[self window] modalDelegate:self didEndSelector:nil 
        contextInfo:nil];
}
@end