/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGWindowController.h"
#import "MGUtils.h"

@implementation MGWindowController
- (id)initWithNibName:(NSString *)aNibName pyClassName:(NSString *)aClassName pyParent:(id)aPyParent;
{
    self = [super initWithWindowNibName:aNibName];
    Class pyClass = [MGUtils classNamed:aClassName];
    py = [[pyClass alloc] initWithCocoa:self pyParent:aPyParent];
    return self;
}

- (oneway void)release
{
    // see MGGUIController
    if ([self retainCount] == 2)
    {
        [py free];
    }
    [super release];
}

- (void)dealloc
{
    // NSLog([NSString stringWithFormat:@"%@ dealloc",[[self class] description]]);
    [py release];
    [super dealloc];
}

- (void)connect
{
    [py connect];
}

- (void)disconnect
{
    [py disconnect];
}

// Python --> Cocoa

- (void)showMessage:(NSString *)msg
{
    NSAlert *a = [NSAlert alertWithMessageText:msg defaultButton:nil alternateButton:nil otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[self window] modalDelegate:self didEndSelector:nil contextInfo:nil];
}

@end
