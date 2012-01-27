/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGFilterBar.h"
#import "MGConst.h"
#import "AMButtonBarItem.h"
#import "Utils.h"

#define MGALL @"all"
#define MGINCOME @"income"
#define MGEXPENSE @"expense"
#define MGTRANSFER @"transfer"
#define MGUNASSIGNED @"unassigned"
#define MGRECONCILED @"reconciled"
#define MGNOTRECONCILED @"not_reconciled"

@implementation MGFilterBar
- (id)initWithPyRef:(PyObject *)aPyRef view:(AMButtonBar *)aView forEntryTable:(BOOL)forEntryTable
{
    PyFilterBar *m = [[PyFilterBar alloc] initWithModel:aPyRef];
    self = [super initWithModel:m view:aView];
    AMButtonBarItem *item = [[[AMButtonBarItem alloc] initWithIdentifier:MGALL] autorelease];
    [item setTitle:TR(@"All")];
    [aView insertItem:item atIndex:0];
    item = [[[AMButtonBarItem alloc] initWithIdentifier:MGINCOME] autorelease];
    [item setTitle:forEntryTable ? TR(@"Increase") : TR(@"Income")];
    [aView insertItem:item atIndex:1];
    item = [[[AMButtonBarItem alloc] initWithIdentifier:MGEXPENSE] autorelease];
    [item setTitle:forEntryTable ? TR(@"Decrease") : TR(@"Expenses")];
    [aView insertItem:item atIndex:2];
    item = [[[AMButtonBarItem alloc] initWithIdentifier:MGTRANSFER] autorelease];
    [item setTitle:TR(@"Transfers")];
    [aView insertItem:item atIndex:3];
    item = [[[AMButtonBarItem alloc] initWithIdentifier:MGUNASSIGNED] autorelease];
    [item setTitle:TR(@"Unassigned")];
    [aView insertItem:item atIndex:4];
    item = [[[AMButtonBarItem alloc] initWithIdentifier:MGRECONCILED] autorelease];
    [item setTitle:TR(@"Reconciled")];
    [aView insertItem:item atIndex:5];
    item = [[[AMButtonBarItem alloc] initWithIdentifier:MGNOTRECONCILED] autorelease];
    [item setTitle:TR(@"Not Reconciled")];
    [aView insertItem:item atIndex:6];
    [aView selectItemWithIdentifier:MGALL];
    [aView setDelegate:self];
    [m bindCallback:createCallback(@"FilterBarView", self)];
    [m release];
    return self;
}

/* HSGUIController */

- (PyFilterBar *)model
{
    return (PyFilterBar *)model;
}

- (AMButtonBar *)view
{
    return (AMButtonBar *)view;
}

/* Delegate */

- (void)buttonBarSelectionDidChange:(NSNotification *)aNotification
{
    NSArray *selectedItems = [[aNotification userInfo] objectForKey:@"selectedItems"];
        NSString *selected = [selectedItems objectAtIndex:0];
        [[self model] setFilterType:selected];
}

/* Python --> Cocoa */

- (void)disableTransfers
{
    [[[[self view] items] objectAtIndex:3] setEnabled:NO];
}

- (void)enableTransfers
{
    [[[[self view] items] objectAtIndex:3] setEnabled:YES];
}

- (void)refresh
{
    [[self view] selectItemWithIdentifier:[[self model] filterType]];
}

@end