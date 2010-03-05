/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGLookup.h"
#import "Utils.h"
#import "NSEventAdditions.h"

@implementation MGLookup
- (id)initWithClassName:(NSString *)aClassName pyParent:(id)aPyParent
{
    self = [super initWithNibName:@"Lookup" pyClassName:aClassName pyParent:aPyParent];
    currentNames = [[NSArray array] retain];
    [self window]; // Initialize the window
    [namesTable setTarget:self];
    [namesTable setDoubleAction:@selector(go:)];
    return self;
}

- (void)dealloc
{
    [currentNames release];
    [super dealloc];
}

- (PyLookup *)py
{
    return (PyLookup *)py;
}

/* Private */
- (void)restoreSelection
{
    [namesTable selectRowIndexes:[NSIndexSet indexSetWithIndex:[[self py] selectedIndex]] byExtendingSelection:NO];
}

/* Actions */
- (IBAction)go:(id)sender
{
    [[self py] go];
}

- (IBAction)updateQuery:(id)sender
{
    [[self py] setSearchQuery:[searchField stringValue]];
}

/* Data source */
- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView
{
    return [currentNames count];
}

- (id)tableView:(NSTableView *)tableView objectValueForTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    return [currentNames objectAtIndex:row];
}

/* Delegate */
- (BOOL)control:(NSControl*)control textView:(NSTextView*)textView doCommandBySelector:(SEL)commandSelector
{
    if (commandSelector == @selector(insertNewline:)) {
        [[self py] go];
        return YES;
    }
    else if(commandSelector == @selector(moveUp:)) {
        NSInteger selected = [namesTable selectedRow];
        if (selected > 0) {
            [namesTable selectRowIndexes:[NSIndexSet indexSetWithIndex:selected-1] byExtendingSelection:NO];
        }
        return YES;
    }
    else if(commandSelector == @selector(moveDown:)) {
        NSInteger selected = [namesTable selectedRow];
        if (selected < [currentNames count]-1) {
            [namesTable selectRowIndexes:[NSIndexSet indexSetWithIndex:selected+1] byExtendingSelection:NO];
        }
        return YES;
    }
    return NO;
}

- (void)tableViewSelectionDidChange:(NSNotification *)notification
{
    NSInteger selected = [namesTable selectedRow];
    [[self py] setSelectedIndex:selected];
}

/* Python --> Cocoa */
- (void)refresh
{
    [currentNames release];
    currentNames = [[[self py] names] retain];
    [namesTable reloadData];
    [self restoreSelection];
    [searchField setStringValue:[[self py] searchQuery]];
}

- (void)show
{
    [self showWindow:self];
    [[self window] makeFirstResponder:searchField];
}

- (void)hide
{
    [self close];
}
@end