/* 
Copyright 2013 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGImportBindingCell.h"

@implementation MGImportBindingCell
- (void)drawInteriorWithFrame:(NSRect)cellFrame inView:(NSView *)controlView
{
    if ([self intValue])
    {
        NSImage *i = [NSImage imageNamed:@"lock_12"];
        [i setFlipped:YES];
        NSSize s = [i size];
        CGFloat w = s.width;
        CGFloat h = s.height;
        CGFloat fx = cellFrame.origin.x;
        CGFloat fy = cellFrame.origin.y;
        CGFloat fw = cellFrame.size.width;
        CGFloat fh = cellFrame.size.height;
        NSRect destRect = NSMakeRect(fx + (fw - w) / 2, fy + (fh - h) / 2, w, h);
        [i drawInRect:destRect fromRect:NSZeroRect operation:NSCompositeSourceOver fraction:1];
    }    
}
@end