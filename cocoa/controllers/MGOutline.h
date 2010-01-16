/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGGUIController.h"
#import "MGOutlineView.h"
#import "PyOutline.h"
#import "MGDocument.h"
#import "NSIndexPathAdditions.h"

@interface MGOutline : MGGUIController {
    MGOutlineView *outlineView;
    NSMutableDictionary *itemData;
    MGDocument *document;
    NSString *autosaveName;
    BOOL stateRestored;
}
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName view:(MGOutlineView *)aOutlineView;

- (MGOutlineView *)outlineView;
- (PyOutline *)py;

/* Private */

- (void)restoreExpandedStates;
- (void)saveExpandedStates;

/* Public */
- (void)refresh;
- (void)startEditing;
- (void)stopEditing;
- (void)setAutosaveName:(NSString *)aAutosaveName;
- (void)updateSelection;

/* Caching */
- (id)property:(NSString *)property valueAtPath:(NSIndexPath *)path;
- (void)setProperty:(NSString *)property value:(id)value atPath:(NSIndexPath *)path;
- (NSString *)stringProperty:(NSString *)property valueAtPath:(NSIndexPath *)path;
- (void)setStringProperty:(NSString *)property value:(NSString *)value atPath:(NSIndexPath *)path;
- (BOOL)boolProperty:(NSString *)property valueAtPath:(NSIndexPath *)path;
- (void)setBoolProperty:(NSString *)property value:(BOOL)value atPath:(NSIndexPath *)path;
- (NSInteger)intProperty:(NSString *)property valueAtPath:(NSIndexPath *)path;
- (void)setIntProperty:(NSString *)property value:(int)value atPath:(NSIndexPath *)path;
- (void)refreshItemAtPath:(NSIndexPath *)path;
@end