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