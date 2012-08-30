/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGBaseView.h"

@implementation MGBaseView

@synthesize wholeView;
@synthesize mainResponder;

- (PyBaseView *)model
{
    return (PyBaseView *)model;
}

- (NSView *)view
{
    return wholeView;
}

- (MGPrintView *)viewToPrint
{
    return nil;
}

- (NSString *)tabIconName
{
    return nil;
}

- (void)setupTableView:(MGTableView *)aTableView
{
    /* Setup a MGTableView programatically with correct bindings and stuff. */
    [aTableView setGridStyleMask:NSTableViewSolidHorizontalGridLineMask|NSTableViewSolidVerticalGridLineMask];
    [aTableView setUsesAlternatingRowBackgroundColors:YES];
    NSUserDefaults *udc = [NSUserDefaultsController sharedUserDefaultsController];
    NSDictionary *options = [NSDictionary dictionaryWithObject:@"vtRowHeightOffset" forKey:NSValueTransformerNameBindingOption];
    [aTableView bind:@"rowHeight" toObject:udc withKeyPath:@"values.TableFontSize" options:options];
}
@end