/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGReport.h"
#import "MGAmountCell.h"
#import "MGTextFieldCell.h"
#import "MGConst.h"
#import "Utils.h"

@implementation MGReport
- (id)initWithPyClassName:(NSString *)aClassName pyParent:(id)aPyParent view:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyClassName:aClassName pyParent:aPyParent view:aOutlineView];
    columns = [[MGColumns alloc] initWithPy:[self py] tableView:aOutlineView];
    [outlineView registerForDraggedTypes:[NSArray arrayWithObject:MGPathPasteboardType]];
    return self;
}

- (void)dealloc
{
    [columns release];
    [super dealloc];
}

- (PyReport *)py
{
    return (PyReport *)py;
}

- (MGColumns *)columns
{
    return columns;
}

/* Overrides */
- (void)refresh
{
    [super refresh];
    NSArray *expandedPaths = [[self py] expandedPaths];
    for (NSArray *arrayPath in expandedPaths) {
        NSIndexPath *path = a2p(arrayPath);
        if (path != nil) {
            [outlineView expandItem:path];
        }
    }
}

/* Actions */
- (IBAction)showSelectedAccount:(id)sender
{
    [[self py] showSelectedAccount];
}

- (IBAction)toggleExcluded:(id)sender
{
    if (toggleExcludedIsEnabled) {
        [[self py] toggleExcluded];
    }
}

- (BOOL)canShowSelectedAccount
{
    return [[self py] canShowSelectedAccount];
}

/* NSOutlineView data source */
- (id)outlineView:(NSOutlineView *)aOutlineView objectValueForTableColumn:(NSTableColumn *)column byItem:(id)item
{
    NSIndexPath *path = item;
    
    // Blank nodes are... well... blank.
    if ([self boolProperty:@"is_blank" valueAtPath:path])
    {
        return nil;
    }
    
    // Don't show values on expanded nodes.
    if ([outlineView isItemExpanded:item] && ![[column identifier] isEqualToString:@"name"])
    {
        return nil;
    }
    
    return [super outlineView:outlineView objectValueForTableColumn:column byItem:item];
}

- (BOOL)outlineView:(NSOutlineView *)aOutlineView writeItems:(NSArray *)items toPasteboard:(NSPasteboard *)pboard
{
    NSIndexPath *path = [items objectAtIndex:0];
    if ([self boolProperty:@"is_account" valueAtPath:path])
    {
        NSData *data = [NSKeyedArchiver archivedDataWithRootObject:path];
        [pboard declareTypes:[NSArray arrayWithObject:MGPathPasteboardType] owner:self];
        [pboard setData:data forType:MGPathPasteboardType];
        return YES;
    }
    return NO;
}

- (NSDragOperation)outlineView:(NSOutlineView *)aOutlineView validateDrop:(id < NSDraggingInfo >)info proposedItem:(id)item 
            proposedChildIndex:(NSInteger)index
{
    NSIndexPath *destPath = item;
    NSPasteboard *pboard = [info draggingPasteboard];
    if ([[pboard types] containsObject:MGPathPasteboardType])
    {
        NSData *data = [pboard dataForType:MGPathPasteboardType];
        NSIndexPath *sourcePath = [NSKeyedUnarchiver unarchiveObjectWithData:data];
        if ([[self py] canMovePath:p2a(sourcePath) toPath:p2a(destPath)])
        {
            if (index != -1)
            {
                [outlineView setDropItem:item dropChildIndex:-1];
            }
            return NSDragOperationMove;
        }
    }
    return NSDragOperationNone;
}

- (BOOL)outlineView:(NSOutlineView *)aOutlineView acceptDrop:(id < NSDraggingInfo >)info item:(id)item childIndex:(NSInteger)index
{
    NSPasteboard *pboard = [info draggingPasteboard];
    NSIndexPath *destPath = item;
    if ([[pboard types] containsObject:MGPathPasteboardType])
    {
        NSData *data = [pboard dataForType:MGPathPasteboardType];
        NSIndexPath *sourcePath = [NSKeyedUnarchiver unarchiveObjectWithData:data];
        [[self py] movePath:p2a(sourcePath) toPath:p2a(destPath)];
    }
    return YES;
}

/* NSOutlineView delegate */
- (void)outlineView:(NSOutlineView *)aOutlineView willDisplayCell:(id)theCell 
     forTableColumn:(NSTableColumn *)tableColumn item:(id)item
{
    NSString *column = [tableColumn identifier];
    NSIndexPath *path = item;
    BOOL isTotal = [self boolProperty:@"is_total" valueAtPath:path];
    NSInteger level = [outlineView levelForItem:item];
    NSInteger row = [outlineView rowForItem:item];
    BOOL isPrinting = [NSPrintOperation currentOperation] != nil;

    if ([column isEqualToString:@"name"])
    {
        MGTextFieldCell *cell = theCell;
        NSFont *font = [cell font];
        NSFontManager *fontManager = [NSFontManager sharedFontManager];
        BOOL isExpandable = [self outlineView:outlineView isItemExpandable:item];
        BOOL isFocused = outlineView == [[outlineView window] firstResponder] && [[outlineView window] isKeyWindow];
        BOOL isSelected = row == [outlineView selectedRow];
        
        // Bold or not bold?
        if (isExpandable || isTotal)
            font = [fontManager convertFont:font toHaveTrait:NSFontBoldTrait];
        else
            font = [fontManager convertFont:font toNotHaveTrait:NSFontBoldTrait];
        
        // Totals are italic and dedented
        if (isTotal && level > 0)
        {
            font = [fontManager convertFont:font toFamily:@"Helvetica"]; // Lucida doesn't have italics
            font = [fontManager convertFont:font toHaveTrait:NSFontItalicTrait];
            [cell setIndent:-[outlineView indentationPerLevel]];
        }
        else
        {
            font = [fontManager convertFont:font toFamily:@"Lucida Grande"];
            font = [fontManager convertFont:font toNotHaveTrait:NSFontItalicTrait];
            [cell setIndent:0];
        }
        
        [cell setFont:font];

        // Arrow
        BOOL isAccount = [self boolProperty:@"is_account" valueAtPath:path];
        if (isAccount && !isPrinting)
        {
            [cell setHasArrow:YES];
            [cell setArrowTarget:self];
            [cell setArrowAction:@selector(showSelectedAccount:)];            
        }
        else
            [cell setHasArrow:NO];
        
        // Gray color with excluded nodes
        BOOL isExcluded = [self boolProperty:@"is_excluded" valueAtPath:path];
        NSColor *textColor = isExcluded ? [NSColor lightGrayColor] : [NSColor blackColor];
        [cell setTextColor:textColor];
        
        // Exclude button
        if (isSelected && !isTotal && !isPrinting)
        {
            NSString *imageName = isExcluded ? @"account_in_16" : @"account_out_16";
            [cell setButtonImageName:imageName];
            [cell setButtonTarget:self];
            [cell setButtonAction:@selector(toggleExcluded:)];
        }
        else
            [cell setButtonImageName:nil];
        
        // Dark background
        [cell setHasDarkBackground:isSelected && isFocused && !isPrinting];
    }
    else if (![column isEqualToString:@"account_number"])
    {
        MGAmountCell *cell = theCell;
        BOOL isSubtotal = [self boolProperty:@"is_subtotal" valueAtPath:path];
    
        // Add total lines
        [cell setTotal:isTotal && level < 2];
        // We also want subtotal lines for group totals (level==2)
        [cell setSubtotal:(isTotal && level == 2) || isSubtotal];
    }
}

- (BOOL)outlineView:(NSOutlineView *)aOutlineView shouldSelectItem:(id)item
{
    NSIndexPath *path = item;
    return ![self boolProperty:@"is_blank" valueAtPath:path];
}

- (BOOL)outlineView:(NSOutlineView *)aOutlineView shouldEditTableColumn:(NSTableColumn *)tableColumn item:(id)item
{
    NSIndexPath *path = item;
    BOOL isTotal = [self boolProperty:@"is_total" valueAtPath:path];
    BOOL isType = [self boolProperty:@"is_type" valueAtPath:path];
    return !isTotal && !isType;
}

/* delegate */
- (BOOL)tableViewHadDeletePressed:(NSTableView *)tableView
{
    if ([[self py] canDeleteSelected])
    {
        [[self py] deleteSelected];
        return YES;
    }
    else
    {
        return NO;
    }
}

- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [outlineView startEditing];
    return YES;
}

- (BOOL)tableViewHadSpacePressed:(NSTableView *)tableView
{
    [[self py] toggleExcluded];
    return YES;
}

- (void)outlineViewWasDoubleClicked:(HSOutlineView *)sender
{
    if ([outlineView clickedRow] != -1)
    {
        [[self py] showSelectedAccount];
    }
}

- (void)outlineViewItemDidExpand:(NSNotification *)notification
{
    NSIndexPath *p = [[notification userInfo] objectForKey:@"NSObject"];
    [[self py] expandPath:p2a(p)];
}

- (void)outlineViewItemDidCollapse:(NSNotification *)notification
{
    NSIndexPath *p = [[notification userInfo] objectForKey:@"NSObject"];
    [[self py] collapsePath:p2a(p)];
}

/* HACK WARNING
 * The code below is hacky because, as always, I couldn't figure out how to do this
 * properly. The problem we're trying to solve here is that the include/exlude button
 * action would be triggered when an unselected row (and thus a row that doesn't display
 * the button) was clicked in the area the button is when the row is selected. This
 * could get pretty annoying. I looked into mouse tracking for a while, but I couldn't
 * fix the problem. So, what I do here is that I disable the action during selection changes.
**/
- (void)outlineViewSelectionIsChanging:(NSNotification *)notification
{
    [super outlineViewSelectionIsChanging:notification];
    toggleExcludedIsEnabled = NO;
}

- (void)outlineViewSelectionDidChange:(NSNotification *)notification
{
    [super outlineViewSelectionDidChange:notification];
    toggleExcludedIsEnabled = YES;
}

/* Python --> Cocoa */
- (void)setColumn:(NSString *)colname visible:(BOOL)visible
{
    NSTableColumn *col = [[self outlineView] tableColumnWithIdentifier:colname];
    if (col == nil)
        return;
    if ([col isHidden] == !visible)
        return;
    [col setHidden:!visible];
}
@end