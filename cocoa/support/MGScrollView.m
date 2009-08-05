/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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
