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
    PyTextField *m = [[PyTextField alloc] initWithModel:aPyRef];
    self = [super initWithModel:m];
    [m bindCallback:createCallback(@"GUIObjectView", self)];
    [NSBundle loadNibNamed:@"SearchField" owner:self];
    [self setView:linkedView];
    return self;
}

- (PyTextField *)model
{
    return (PyTextField *)model;
}

/* Action */

- (IBAction)changeQuery:(id)sender
{
    NSString *query = [linkedView stringValue];
    [[self model] setText:query];
}

/* Python callbacks */

- (void)refresh
{
    [linkedView setStringValue:[[self model] text]];
}

@end