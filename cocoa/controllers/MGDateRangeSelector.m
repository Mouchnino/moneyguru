/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGDateRangeSelector.h"
#import "MGConst.h"
#import "Utils.h"
#import "MGAppDelegate.h"

@implementation MGDateRangeSelector
- (id)initWithPyParent:(id)aPyParent
{
    self = [super initWithPyClassName:@"PyDateRangeSelector" pyParent:aPyParent];
    [NSBundle loadNibNamed:@"DateRangeSelector" owner:self];
    /* In popups, there's the invisible first item, which is why we start our indexing at 8! */
    NSMenuItem *custom1 = [dateRangePopUp itemAtIndex:8];
    NSMenuItem *custom2 = [dateRangePopUp itemAtIndex:9];
    NSMenuItem *custom3 = [dateRangePopUp itemAtIndex:10];
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
    NSRect convertedFrame = [dateRangePopUp convertRect:[dateRangePopUp bounds] toView:[[view window] contentView]];
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

/* Actions */
- (IBAction)segmentClicked:(id)sender
{
    NSInteger index = [segmentedControl selectedSegment];
    if (index == 0) {
        [[self py] selectPrevDateRange];
    }
    else if (index == 2) {
        [[self py] selectNextDateRange];
    }
}

- (IBAction)selectMonthRange:(id)sender
{
    [[self py] selectMonthRange];
}

- (IBAction)selectNextDateRange:(id)sender
{
    [[self py] selectNextDateRange];
}

- (IBAction)selectPrevDateRange:(id)sender
{
    [[self py] selectPrevDateRange];
}

- (IBAction)selectTodayDateRange:(id)sender
{
    [[self py] selectTodayDateRange];
}

- (IBAction)selectQuarterRange:(id)sender
{
    [[self py] selectQuarterRange];
}

- (IBAction)selectYearRange:(id)sender
{
    [[self py] selectYearRange];
}

- (IBAction)selectYearToDateRange:(id)sender
{
    [[self py] selectYearToDateRange];
}

- (IBAction)selectRunningYearRange:(id)sender
{
    [[self py] selectRunningYearRange];
}

- (IBAction)selectAllTransactionsRange:(id)sender
{
    [[self py] selectAllTransactionsRange];
}

- (IBAction)selectCustomDateRange:(id)sender
{
    [[self py] selectCustomDateRange];
}

- (IBAction)selectSavedCustomRange:(id)sender
{
    NSInteger slot = [(NSMenuItem *)sender tag] - MGCustomSavedRangeStart;
    [[self py] selectSavedRange:slot];
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
    [dateRangePopUp setTitle:[[self py] display]];
    BOOL canNavigate = [[self py] canNavigate];
    [segmentedControl setEnabled:canNavigate forSegment:0];
    [segmentedControl setEnabled:canNavigate forSegment:2];
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