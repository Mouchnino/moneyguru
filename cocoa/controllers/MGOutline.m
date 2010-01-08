/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGOutline.h"
#import "Utils.h"

#define CHILDREN_COUNT_PROPERTY @"children_count"

@implementation MGOutline

- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName view:(MGOutlineView *)aOutlineView
{
    self = [super initWithPyClassName:aClassName pyParent:[aDocument py]];
    document = [aDocument retain];
    itemData = [[NSMutableDictionary dictionary] retain];
    outlineView = aOutlineView;
    [outlineView setDataSource:self];
    [outlineView setDelegate:self];
    autosaveName = nil;
    stateRestored = NO;
    return self;
}

- (void)dealloc
{
    if (stateRestored) // if it wasn't restored, it means that the outline was never refreshed with any content. don't save
    {
        [self saveExpandedStates];
    }
    [itemData release];
    [document release];
    [super dealloc];
}

- (MGOutlineView *)outlineView
{
    return outlineView;
}

- (PyOutline *)py
{
    return (PyOutline *)py;
}

/* Private */

- (void)restoreExpandedStates
{
    if ((autosaveName == nil) || (![outlineView numberOfRows]))
    {
        // Don't try to restore anything if we don't have an autosave name, or if the outline is empty.
        return;
    }
    stateRestored = YES;
    NSString *key = [NSString stringWithFormat:@"%@.ExpandedItems",autosaveName];
    NSArray *expandedPaths = [document defaultForKey:key];
    if (expandedPaths == nil)
    {
        return;
    }
    NSEnumerator *e = [expandedPaths objectEnumerator];
    NSString *archivedPath;
    while (archivedPath = [e nextObject])
    {
        NSIndexPath *path = [Utils string2IndexPath:archivedPath];
        if (path != nil)
        {
            [outlineView expandItem:path];
        }
    }
}

- (void)saveExpandedStates
{
    if (autosaveName == nil)
    {
        return;
    }
    NSMutableArray *expandedPaths = [NSMutableArray array];
    for (int i=0; i<[outlineView numberOfRows]; i++)
    {
        NSIndexPath *path = [outlineView itemAtRow:i];
        if ([outlineView isItemExpanded:path])
        {
            [expandedPaths addObject:[Utils indexPath2String:path]];
        }
   }
   NSString *key = [NSString stringWithFormat:@"%@.ExpandedItems",autosaveName];
   [document setDefault:expandedPaths forKey:key];
}

/* Public */

- (void)refresh
{
    [itemData removeAllObjects];
    [outlineView reloadData];
    if (!stateRestored)
    {
        [self restoreExpandedStates];
    }
    [self updateSelection];
}

- (void)startEditing
{
    [outlineView startEditing];
}

- (void)stopEditing
{
    [outlineView stopEditing];
}

- (void)updateSelection
{
    [outlineView updateSelection];
}

- (void)setAutosaveName:(NSString *)aAutosaveName
{
    autosaveName = aAutosaveName;
}

/* Caching */
- (id)property:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    NSMutableDictionary *props = [itemData objectForKey:path];
    id value = [props objectForKey:property];
    if (value == nil)
    {
        value = [[self py] property:property valueAtPath:p2a(path)];
        if (value == nil)
        {
            value = [NSNull null];
        }
        [props setObject:value forKey:property];
    }
    if (value == [NSNull null])
    {
        value = nil;
    }
    return value;
}

- (void)setProperty:(NSString *)property value:(id)value atPath:(NSIndexPath *)path
{
    NSMutableDictionary *props = [itemData objectForKey:path];
    [props removeObjectForKey:property];
    [[self py] setProperty:property value:value atPath:p2a(path)];
}

- (NSString *)stringProperty:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    return [self property:property valueAtPath:path];
}

- (void)setStringProperty:(NSString *)property value:(NSString *)value atPath:(NSIndexPath *)path
{
    [self setProperty:property value:value atPath:path];
}

- (BOOL)boolProperty:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    NSNumber *value = [self property:property valueAtPath:path];
    return [value boolValue];
}

- (void)setBoolProperty:(NSString *)property value:(BOOL)value atPath:(NSIndexPath *)path
{
    [self setProperty:property value:[NSNumber numberWithBool:value] atPath:path];
}

- (int)intProperty:(NSString *)property valueAtPath:(NSIndexPath *)path
{
    NSNumber *value = [self property:property valueAtPath:path];
    return [value intValue];
}

- (void)setIntProperty:(NSString *)property value:(int)value atPath:(NSIndexPath *)path
{
    [self setProperty:property value:[NSNumber numberWithInt:value] atPath:path];
}

- (void)refreshItemAtPath:(NSIndexPath *)path
{
    NSMutableDictionary *props = [itemData objectForKey:path];
    [props removeAllObjects];
}

/* NSOutlineView data source */

- (int)outlineView:(NSOutlineView *)outlineView numberOfChildrenOfItem:(id)item
{
    return [self intProperty:CHILDREN_COUNT_PROPERTY valueAtPath:(NSIndexPath *)item];
}

- (id)outlineView:(NSOutlineView *)outlineView child:(int)index ofItem:(id)item
{
    NSIndexPath *parent = item;
    NSIndexPath *child = parent == nil ? [NSIndexPath indexPathWithIndex:index] : [parent indexPathByAddingIndex:index];
    if ([itemData objectForKey:child] == nil)
    {
        // Note: in general, the dictionary doesn't retain the keys that are given to it, but copies
        // of them. In our case, since a copy of an index path is the same index path, using an index
        // path as a key in actually retains the index path.
        [itemData setObject:[NSMutableDictionary dictionary] forKey:child];
    }
    return child;
}

- (BOOL)outlineView:(NSOutlineView *)theOutlineView isItemExpandable:(id)item
{
    return [self outlineView:outlineView numberOfChildrenOfItem:item] > 0;
}

- (BOOL)outlineView:(NSOutlineView *)outlineView shouldEditTableColumn:(NSTableColumn *)column item:(id)item
{
    return [[self py] canEditProperty:[column identifier] atPath:p2a((NSIndexPath *)item)];
}

- (id)outlineView:(NSOutlineView *)outlineView objectValueForTableColumn:(NSTableColumn *)column byItem:(id)item
{
    return [self property:[column identifier] valueAtPath:(NSIndexPath *)item];
}

- (void)outlineView:(NSOutlineView *)outlineView setObjectValue:(id)value forTableColumn:(NSTableColumn *)column byItem:(id)item
{
    [self setProperty:[column identifier] value:value atPath:(NSIndexPath *)item];
}

/* NSOutlineView delegate */

- (NSIndexPath *)selectedIndexPath
{
    return a2p([[self py] selectedPath]);
}

/* We need to change the py selection at both IsChanging and DidChange. We need to set the
py selection at IsChanging before of the arrow clicking. The action launched by this little arrow
is performed before DidChange. However, when using the arrow to change the selection, IsChanging is
never called
*/
- (void)outlineViewSelectionIsChanging:(NSNotification *)notification
{
    NSArray *indexPath = p2a([outlineView itemAtRow:[outlineView selectedRow]]);
    if (![indexPath isEqualTo:[[self py] selectedPath]])
        [[self py] setSelectedPath:indexPath];
}

- (void)outlineViewSelectionDidChange:(NSNotification *)notification
{
    NSArray *indexPath = p2a([outlineView itemAtRow:[outlineView selectedRow]]);
    if (![indexPath isEqualTo:[[self py] selectedPath]])
        [[self py] setSelectedPath:indexPath];
}

- (void)outlineViewDidEndEditing:(MGOutlineView *)outlineView
{
    [[self py] saveEdits];
}

- (void)outlineViewCancelsEdition:(MGOutlineView *)outlineView
{
    [[self py] cancelEdits];
}
@end