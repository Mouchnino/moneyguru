/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTransparentButtonCell.h"
#import "NSCellAdditions.h"

@implementation MGTransparentButtonCell
- (void)drawBezelWithFrame:(NSRect)frame inView:(NSView *)controlView {
    [self drawTransparentBezelWithFrame:frame inView:controlView withLeftSide:NO];
}
@end

@implementation MGTransparentButtonCellWithLeftSide
- (void)drawBezelWithFrame:(NSRect)frame inView:(NSView *)controlView {
    [self drawTransparentBezelWithFrame:frame inView:controlView withLeftSide:YES];
}
@end

@implementation MGTransparentPopUpButtonCell
- (void)drawInteriorWithFrame:(NSRect)frame inView:(NSView *)controlView
{
    [super drawInteriorWithFrame:frame inView:controlView];
    // This arrow drawing override below is because Tiger somehow draw the arrow all wrong, and
    // flipped with the settings we have for the date range popup.
    NSImage *i = [NSImage imageNamed:@"nav_down_6"];
    [i setFlipped:YES];
    float iw = [i size].width;
    float ih = [i size].height;
    float fx = frame.origin.x;
    float fy = frame.origin.y;
    float fw = frame.size.width;
    float fh = frame.size.height;
    NSRect arrowRect = NSMakeRect(fx + fw - iw - 6, fy + (fh - ih) / 2, iw, ih);
    [i drawInRect:arrowRect fromRect:NSZeroRect operation:NSCompositeSourceOver fraction:1];
}
@end