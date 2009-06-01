#import <Cocoa/Cocoa.h>
#import "MGTableWithSplitsPrint.h"

@interface MGEntryPrint : MGTableWithSplitsPrint
{
    NSView *graphView;
    float graphY;
    float graphHeight;
    BOOL graphVisible;
}
- (id)initWithPyParent:(id)pyParent tableView:(NSTableView *)aTableView graphView:(NSView *)aGraphView;
@end