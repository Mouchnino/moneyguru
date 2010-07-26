/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>

/*
    This structure is to define constants describing table columns (it's easier to maintain in code
    than in XIB files).
*/
typedef struct {
    NSString *attrname;
    NSString *title; /* Untranslated. It will be translated on column instantiation. */
    NSUInteger defaultWidth;
    NSUInteger minWidth;
    NSUInteger maxWidth;
    BOOL sortable;
    Class cellClass;
} MGColumnDef;

@interface MGColumns : NSObject
{
    id py; /* We can't have a specific class here because we support both PyTable and PyOutline */
    NSTableView *tableView;
    BOOL isRestoring;
}
- (id)initWithPy:(id)aPy tableView:(NSTableView *)aTableView;
- (void)initializeColumns:(MGColumnDef *)columns;
- (void)restoreColumns;
@end