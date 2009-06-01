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