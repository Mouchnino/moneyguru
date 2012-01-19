/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGLookup.h"
#import "Utils.h"
#import "ObjP.h"
#import "NSEventAdditions.h"

@implementation MGLookup
- (id)initWithPy:(id)aPy
{
    self = [super initWithWindowNibName:@"Lookup"];
    PyObject *pRef = getHackedPyRef(aPy);
    model = [[PyLookup alloc] initWithModel:pRef];
    OBJP_LOCKGIL;
    Py_DECREF(pRef);
    OBJP_UNLOCKGIL;
    [model bindCallback:createCallback(@"LookupView", self)];
    currentNames = [[NSArray array] retain];
    [self window]; // Initialize the window
    [namesTable setTarget:self];
    [namesTable setDoubleAction:@selector(go:)];
    return self;
}

- (void)dealloc
{
    [currentNames release];
    [model release];
    [super dealloc];
}

/* Private */
- (void)restoreSelection
{
    [namesTable selectRowIndexes:[NSIndexSet indexSetWithIndex:[model selectedIndex]] byExtendingSelection:NO];
}

/* Actions */
- (IBAction)go:(id)sender
{
    [model go];
}

- (IBAction)updateQuery:(id)sender
{
    [model setSearchQuery:[searchField stringValue]];
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
        [model go];
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
    [model setSelectedIndex:selected];
}

/* Python --> Cocoa */
- (void)refresh
{
    [currentNames release];
    currentNames = [[model names] retain];
    [namesTable reloadData];
    [self restoreSelection];
    [searchField setStringValue:[model searchQuery]];
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