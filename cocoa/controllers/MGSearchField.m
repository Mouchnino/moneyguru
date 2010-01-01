/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGSearchField.h"

@implementation MGSearchField
- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PySearchField" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"SearchField" owner:self];
    return self;
}

/* MGGUIController */

- (PySearchField *)py
{
    return (PySearchField *)py;
}

- (NSView *)view
{
    return view;
}

/* Action */

- (IBAction)changeQuery:(id)sender
{
    NSString *query = [view stringValue];
    [[self py] setQuery:query];
}

/* Python callbacks */

- (void)refresh
{
    [view setStringValue:[[self py] query]];
}

@end