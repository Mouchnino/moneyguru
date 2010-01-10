/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGUIController.h"
#import "MGUtils.h"

@implementation MGGUIController

- (id)init
{
    // If you use this initialisation, you get a nil py
    return [super init];
}

- (id)initWithPyClassName:(NSString *)aClassName pyParent:(id)aPyParent
{
    self = [super init];
    Class pyClass = [MGUtils classNamed:aClassName];
    py = [[pyClass alloc] initWithCocoa:self pyParent:aPyParent];
    return self;
}

- (oneway void)release
{
    // The py side hold one reference, which is why when we see that we only have 1 reference left,
    // we must break our reference in the py side (free). We also can't call retainCount after
    // [super release], because we might be freed. If the retainCount is 2 before the release, it
    // will be 1 afterwards.
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

- (NSView *)view
{
    // abstract
    return nil;
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
    NSAlert *a = [NSAlert alertWithMessageText:msg defaultButton:nil alternateButton:nil 
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[[self view] window] modalDelegate:self didEndSelector:nil 
        contextInfo:nil];
}

@end
