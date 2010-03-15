/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGDateRangeSelector.h"
#import "Utils.h"

@implementation MGDateRangeSelector
- (id)initWithPyParent:(id)aPyParent view:(MGDateRangeSelectorView *)aView
{
    self = [super initWithPyClassName:@"PyDateRangeSelector" pyParent:aPyParent];
    view = aView;
    return self;
}

/* HSGUIController */
- (PyDateRangeSelector *)py
{
    return (PyDateRangeSelector *)py;
}

- (NSView *)view
{
    return view;
}

/* Public */
- (void)animate:(BOOL)forward
{
    CGFloat PADDING = 3;
    NSRect convertedFrame = [[view dateRangePopUp] convertRect:[[view dateRangePopUp] bounds] toView:[[[self view] window] contentView]];
    convertedFrame.size.width -= PADDING *2;
    convertedFrame.size.height -= PADDING *2;
    convertedFrame.origin.x += PADDING;
    convertedFrame.origin.y += PADDING;
    NSImageView *imageView = [[[NSImageView alloc] initWithFrame:convertedFrame] autorelease];
    [imageView setImageAlignment:forward ? NSImageAlignTopRight : NSImageAlignTopLeft];
    [imageView setImageScaling:NSScaleProportionally];
    [imageView setImage:[NSImage imageNamed:forward ? @"forward_32" : @"backward_32"]];
    [[[[self view] window] contentView] addSubview:imageView positioned:NSWindowAbove relativeTo:nil];
    NSMutableDictionary *animData = [NSMutableDictionary dictionary];
    [animData setObject:imageView forKey:NSViewAnimationTargetKey];
    [animData setObject:NSViewAnimationFadeOutEffect forKey:NSViewAnimationEffectKey];
    NSMutableArray *animations = [NSMutableArray arrayWithObject:animData];
    NSViewAnimation *anim = [[NSViewAnimation alloc] initWithViewAnimations:animations];
    [anim setDuration:0.5];
    [anim setAnimationCurve:NSAnimationLinear];
    [anim setDelegate:self];
    [anim startAnimation];
}

- (void)refresh
{
    [[view dateRangePopUp] setTitle:[[self py] display]];
    BOOL canNavigate = [[self py] canNavigate];
    [[view prevDateRangeButton] setEnabled:canNavigate];
    [[view nextDateRangeButton] setEnabled:canNavigate];
}

/* Delegate */
- (void)animationDidEnd:(NSAnimation *)animation
{
    // Remove all views used by the animation from their superviews
    NSDictionary *animData;
    NSEnumerator *e = [[(NSViewAnimation *)animation viewAnimations] objectEnumerator];
    while (animData = [e nextObject]) {
        NSView *theView = [animData objectForKey:NSViewAnimationTargetKey];
        [theView removeFromSuperview];
    }
    [animation release];
}
@end