#import <Cocoa/Cocoa.h>
#import "NSTableViewAdditions.h"
#import "NSIndexPathAdditions.h"

@interface MGOutlineView : NSOutlineView
{
    BOOL manualEditionStop;
    NSEvent *eventToIgnore;
}
- (void)selectPath:(NSIndexPath *)aPath;
- (void)stopEditing;
- (void)updateSelection;
- (void)ignoreEventForEdition:(NSEvent *)aEvent;
@end

@interface NSObject(MGOutlineViewDelegate)
- (NSIndexPath *)selectedIndexPath;
- (void)outlineViewDidEndEditing:(MGOutlineView *)outlineView;
- (void)outlineViewCancelsEdition:(MGOutlineView *)outlineView;
- (void)outlineViewWasDoubleClicked:(MGOutlineView *)outlineView;
@end

