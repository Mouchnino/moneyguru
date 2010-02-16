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

- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName view:(HSOutlineView *)aOutlineView
{
    self = [super initWithPyClassName:aClassName pyParent:[aDocument py] view:aOutlineView];
    document = [aDocument retain];
    autosaveName = nil;
    stateRestored = NO;
    return self;
}

- (void)dealloc
{
    // if it wasn't restored, it means that the outline was never refreshed with any content. don't save
    if (stateRestored) {
        [self saveExpandedStates];
    }
    [document release];
    [super dealloc];
}

/* Private */
- (void)restoreExpandedStates
{
    if ((autosaveName == nil) || (![outlineView numberOfRows])) {
        // Don't try to restore anything if we don't have an autosave name, or if the outline is empty.
        return;
    }
    stateRestored = YES;
    NSString *key = [NSString stringWithFormat:@"%@.ExpandedItems",autosaveName];
    NSArray *expandedPaths = [document defaultForKey:key];
    if (expandedPaths == nil) {
        return;
    }
    for (NSString *archivedPath in expandedPaths) {
        NSIndexPath *path = [Utils string2IndexPath:archivedPath];
        if (path != nil) {
            [outlineView expandItem:path];
        }
    }
}

- (void)saveExpandedStates
{
    if (autosaveName == nil) {
        return;
    }
    NSMutableArray *expandedPaths = [NSMutableArray array];
    for (int i=0; i<[outlineView numberOfRows]; i++)
    {
        NSIndexPath *path = [outlineView itemAtRow:i];
        if ([outlineView isItemExpanded:path]) {
            [expandedPaths addObject:[Utils indexPath2String:path]];
        }
   }
   NSString *key = [NSString stringWithFormat:@"%@.ExpandedItems",autosaveName];
   [document setDefault:expandedPaths forKey:key];
   [[NSUserDefaults standardUserDefaults] synchronize];
}

/* Public */

- (void)refresh
{
    [super refresh];
    if (!stateRestored) {
        [self restoreExpandedStates];
    }
}

- (void)setAutosaveName:(NSString *)aAutosaveName
{
    autosaveName = aAutosaveName;
}
@end