/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGDateRangeSelector.h"
#import "Utils.h"
#import "MGAppDelegate.h"

@implementation MGDateRangeSelector
- (id)initWithPyParent:(id)aPyParent dateRangeView:(MGDateRangeSelectorView *)aView
{
    self = [super initWithPyClassName:@"PyDateRangeSelector" pyParent:aPyParent];
    view = aView;
    /* In popups, there's the invisible first item, which is why we start our indexing at 8! */
    NSMenuItem *custom1 = [[view dateRangePopUp] itemAtIndex:8];
    NSMenuItem *custom2 = [[view dateRangePopUp] itemAtIndex:9];
    NSMenuItem *custom3 = [[view dateRangePopUp] itemAtIndex:10];
    customRangeItems = [[NSArray arrayWithObjects:custom1, custom2, custom3, nil] retain];
    return self;
}

- (void)dealloc
{
    [customRangeItems release];
    [super dealloc];
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

/* Delegate */
- (void)animationDidEnd:(NSAnimation *)animation
{
    // Remove all views used by the animation from their superviews
    for (NSDictionary *animData in [(NSViewAnimation *)animation viewAnimations]) {
        NSView *theView = [animData objectForKey:NSViewAnimationTargetKey];
        [theView removeFromSuperview];
    }
    [animation release];
}

- (void)animateForward
{
    [self animate:YES];
}

- (void)animateBackward
{
    [self animate:NO];
}

- (void)refresh
{
    [[view dateRangePopUp] setTitle:[[self py] display]];
    BOOL canNavigate = [[self py] canNavigate];
    [[view prevDateRangeButton] setEnabled:canNavigate];
    [[view nextDateRangeButton] setEnabled:canNavigate];
}

- (void)refreshCustomRanges
{
    NSArray *names = [[self py] customRangeNames];
    MGAppDelegate *app = [NSApp delegate];
    for (NSInteger i=0; i<[names count]; i++) {
        id item = [names objectAtIndex:i];
        NSString *name = item == [NSNull null] ? nil : item;
        [app setCustomDateRangeName:name atSlot:i];
        NSMenuItem *popupItem = [customRangeItems objectAtIndex:i];
        if (name != nil) {
            [popupItem setHidden:NO];
            [popupItem setTitle:name];
        }
        else {
            [popupItem setHidden:YES];
        }
    }
}
@end