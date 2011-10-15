/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGSearchField.h"

@implementation MGSearchField
- (id)initWithPy:(id)aPy
{
    self = [super initWithPy:aPy];
    [NSBundle loadNibNamed:@"SearchField" owner:self];
    [self setView:linkedView];
    return self;
}

/* HSGUIController */

- (PySearchField *)py
{
    return (PySearchField *)py;
}

/* Action */

- (IBAction)changeQuery:(id)sender
{
    NSString *query = [linkedView stringValue];
    [[self py] setQuery:query];
}

/* Python callbacks */

- (void)refresh
{
    [linkedView setStringValue:[[self py] query]];
}

@end