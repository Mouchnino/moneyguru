#import "MGScrollView.h"

@implementation MGScrollView
- (void)tile
{
    [super tile];
    
    // Make sure the view is placed at the top of the scroll view
    NSRect documentRect = [[self documentView] frame];
    NSRect contentRect = [[self contentView] frame];
    if (NSHeight(documentRect) < NSHeight(contentRect))
    {
        contentRect.size.height = NSHeight(documentRect);
        [[self contentView] setFrame:contentRect];
    }
}

@end
