#import <Cocoa/Cocoa.h>

@interface NSCell(NSCellAdditions)
- (void)drawTransparentBezelWithFrame:(NSRect)frame inView:(NSView *)controlView withLeftSide:(BOOL)withLeftSide;
@end