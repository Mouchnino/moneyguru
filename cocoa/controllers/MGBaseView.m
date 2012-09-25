/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBaseView.h"

@implementation MGBaseView

@synthesize mainResponder;

/* Overrides */
- (PyBaseView *)model
{
    return (PyBaseView *)model;
}

- (void)setView:(NSView *)aView
{
    [super setView:aView];
    if (aView != nil) {
        [self.view setPostsFrameChangedNotifications:YES];
        [[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(viewFrameChanged:)
            name:NSViewFrameDidChangeNotification object:self.view];
    }
}

/* Public */
- (MGPrintView *)viewToPrint
{
    return nil;
}

- (NSString *)tabIconName
{
    return nil;
}

/* This is called once, the first time that self.view's frame is changed (thus indicating that we
   have our "real" size now and that it's safe to restore subviews size).
*/
- (void)applySubviewsSizeRestoration {}

- (void)setupTableView:(MGTableView *)aTableView
{
    /* Setup a MGTableView programatically with correct bindings and stuff. */
    [aTableView setGridStyleMask:NSTableViewSolidHorizontalGridLineMask|NSTableViewSolidVerticalGridLineMask];
    [aTableView setUsesAlternatingRowBackgroundColors:YES];
    NSUserDefaults *udc = [NSUserDefaultsController sharedUserDefaultsController];
    NSDictionary *options = [NSDictionary dictionaryWithObject:@"vtRowHeightOffset" forKey:NSValueTransformerNameBindingOption];
    [aTableView bind:@"rowHeight" toObject:udc withKeyPath:@"values.TableFontSize" options:options];
}

/* Notifications */
- (void)viewFrameChanged:(NSNotification *)aNotification
{
    [[NSNotificationCenter defaultCenter] removeObserver:self name:NSViewFrameDidChangeNotification
        object:self.view];
    [self.view setPostsFrameChangedNotifications:NO];
    [self applySubviewsSizeRestoration];
}

/* model --> view */
- (void)updateVisibility {}
@end