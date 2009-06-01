#import "MGImportBindingCell.h"

@implementation MGImportBindingCell
- (void)drawInteriorWithFrame:(NSRect)cellFrame inView:(NSView *)controlView
{
    if ([self intValue])
    {
        NSImage *i = [NSImage imageNamed:@"lock_12"];
        [i setFlipped:YES];
        NSSize s = [i size];
        float w = s.width;
        float h = s.height;
        float fx = cellFrame.origin.x;
        float fy = cellFrame.origin.y;
        float fw = cellFrame.size.width;
        float fh = cellFrame.size.height;
        NSRect destRect = NSMakeRect(fx + (fw - w) / 2, fy + (fh - h) / 2, w, h);
        [i drawInRect:destRect fromRect:NSZeroRect operation:NSCompositeSourceOver fraction:1];
    }    
}
@end