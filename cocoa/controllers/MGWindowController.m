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
