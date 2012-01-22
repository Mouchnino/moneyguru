/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGDateRangeSelector.h"
#import "MGConst.h"
#import "Utils.h"
#import "MGAppDelegate.h"

@implementation MGDateRangeSelector
- (id)initWithPyRef:(PyObject *)aPyRef
{
    PyDateRangeSelector *m = [[PyDateRangeSelector alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"DateRangeSelectorView", self)];
    [m release];
    [NSBundle loadNibNamed:@"DateRangeSelector" owner:self];
    [self setView:linkedView];
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

- (PyDateRangeSelector *)model
{
    return (PyDateRangeSelector *)model;
}

/* Public */
- (void)animate:(BOOL)forward
{
    CGFloat PADDING = 3;
    NSRect convertedFrame = [dateRangePopUp convertRect:[dateRangePopUp bounds] toView:[[[self view] window] contentView]];
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
        [[self model] selectPrevDateRange];
    }
    else if (index == 2) {
        [[self model] selectNextDateRange];
    }
}

- (IBAction)selectMonthRange:(id)sender
{
    [[self model] selectMonthRange];
}

- (IBAction)selectNextDateRange:(id)sender
{
    [[self model] selectNextDateRange];
}

- (IBAction)selectPrevDateRange:(id)sender
{
    [[self model] selectPrevDateRange];
}

- (IBAction)selectTodayDateRange:(id)sender
{
    [[self model] selectTodayDateRange];
}

- (IBAction)selectQuarterRange:(id)sender
{
    [[self model] selectQuarterRange];
}

- (IBAction)selectYearRange:(id)sender
{
    [[self model] selectYearRange];
}

- (IBAction)selectYearToDateRange:(id)sender
{
    [[self model] selectYearToDateRange];
}

- (IBAction)selectRunningYearRange:(id)sender
{
    [[self model] selectRunningYearRange];
}

- (IBAction)selectAllTransactionsRange:(id)sender
{
    [[self model] selectAllTransactionsRange];
}

- (IBAction)selectCustomDateRange:(id)sender
{
    [[self model] selectCustomDateRange];
}

- (IBAction)selectSavedCustomRange:(id)sender
{
    NSInteger slot = [(NSMenuItem *)sender tag] - MGCustomSavedRangeStart;
    [[self model] selectSavedRange:slot];
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
    [dateRangePopUp setTitle:[[self model] display]];
    BOOL canNavigate = [[self model] canNavigate];
    [segmentedControl setEnabled:canNavigate forSegment:0];
    [segmentedControl setEnabled:canNavigate forSegment:2];
}

- (void)refreshCustomRanges
{
    NSArray *names = [[self model] customRangeNames];
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