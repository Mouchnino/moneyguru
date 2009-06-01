#import <Cocoa/Cocoa.h>
#import "MGGUIController.h"
#import "MGOutlineView.h"
#import "PyOutline.h"
#import "MGDocument.h"
#import "NSIndexPathAdditions.h"

@interface MGOutline : MGGUIController {
    IBOutlet MGOutlineView *outlineView;
    IBOutlet NSView *wholeView;
    
    NSMutableDictionary *itemData;
    MGDocument *document;
    NSString *autosaveName;
    BOOL stateRestored;
}
- (id)initWithDocument:(MGDocument *)aDocument pyClassName:(NSString *)aClassName;

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
- (int)intProperty:(NSString *)property valueAtPath:(NSIndexPath *)path;
- (void)setIntProperty:(NSString *)property value:(int)value atPath:(NSIndexPath *)path;
- (void)refreshItemAtPath:(NSIndexPath *)path;
@end