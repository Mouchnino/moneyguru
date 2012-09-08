/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSearchField.h"
#import "HSPyUtil.h"

@implementation MGSearchField
- (id)initWithPyRef:(PyObject *)aPyRef
{
    NSSearchField *searchView = [[NSSearchField alloc] init];
    [searchView setFrame:NSMakeRect(0, 0, 132, 24)];
    [[searchView cell] setSendsSearchStringImmediately:NO];
    [[searchView cell] setSendsWholeSearchString:YES];
    PyTextField *m = [[PyTextField alloc] initWithModel:aPyRef];
    self = [super initWithModel:m view:[searchView autorelease]];
    [m bindCallback:createCallback(@"GUIObjectView", self)];
    [m release];
    return self;
}

- (NSSearchField *)view
{
    return (NSSearchField *)view;
}

- (void)setView:(NSSearchField *)aView
{
    if ([self view] != nil) {
        [[self view] setTarget:nil];
    }
    [super setView:aView];
    if (aView != nil) {
        /* The action on a NSSearchField happens when escape is pressed, something that isn't covered
           by controlTextDidEndEditing: in HSTextField.
        */
        [aView setAction:@selector(changeQuery)];
        [aView setTarget:self];
    }
}

/* Action */
- (void)changeQuery
{
    [[self model] setText:[[self view] stringValue]];
}
@end