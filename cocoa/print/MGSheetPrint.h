#import <Cocoa/Cocoa.h>
#import "MGOutlinePrint.h"
#import "MGDoubleView.h"

@interface MGSheetPrint : MGOutlinePrint
{
    NSView *graphView;
    MGDoubleView *pieViews;
    int piePage;
    int graphPage;
    BOOL graphVisible;
    BOOL pieVisible;
}
- (id)initWithPyParent:(id)pyParent outlineView:(NSOutlineView *)aOutlineView 
    graphView:(NSView *)aGraphView pieViews:(MGDoubleView *)aPieViews;
@end