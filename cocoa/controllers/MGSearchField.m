/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSearchField.h"
#import "Utils.h"

@implementation MGSearchField
- (id)initWithPyRef:(PyObject *)aPyRef
{
    NSSearchField *searchView = [[NSSearchField alloc] init];
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
    [super setView:aView];
    /* The action on a NSSearchField happens when escape is pressed, something that isn't covered
       by controlTextDidEndEditing: in HSTextField.
    */
    [aView setAction:@selector(changeQuery:)];
    [aView setTarget:self];
}

/* Action */
- (IBAction)changeQuery:(id)sender
{
    [[self model] setText:[[self view] stringValue]];
}
@end