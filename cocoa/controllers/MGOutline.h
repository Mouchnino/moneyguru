/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "HSOutline.h"

@interface MGOutline : HSOutline {
    // MGDocument *document;
    NSString *autosaveName;
    BOOL stateRestored;
}
- (id)initWithPyParent:(id)aPyParent pyClassName:(NSString *)aClassName view:(HSOutlineView *)aOutlineView;

/* Private */
// XXX Push that logic in the core code
// - (void)restoreExpandedStates;
// - (void)saveExpandedStates;

/* Public */
- (void)setAutosaveName:(NSString *)aAutosaveName;
@end