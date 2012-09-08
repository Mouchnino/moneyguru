/* 
Copyright 2012 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGMainWindow.h"
#import "MGConst.h"
#import "NSEventAdditions.h"

@implementation MGMainWindow
- (MGMainWindowController *)delegate
{
    return (MGMainWindowController *)[super delegate];
}

- (void)setDelegate:(MGMainWindowController *)aDelegate
{
    [super setDelegate:aDelegate];
}

- (void)performClose:(id)sender
{
    if ([sender tag] == MGCloseWindowMenuItem) {
        // Force the close of the whole window.
        [super performClose:sender];
    }
    else {
        // Close tab if there's more than one.
        MGMainWindowController *delegate = [self delegate];
        if ([delegate openedTabCount] > 1) {
            [delegate closeActiveTab];
        }
        else {
            [super performClose:sender];
        }
    }
}

- (BOOL)performKeyEquivalent:(NSEvent *)event 
{
    BOOL isEditing = [[[self firstResponder] class] isSubclassOfClass:[NSTextView class]];
    SEL action = nil;
    if ((!isEditing) && ([event modifierKeysFlags] == (NSCommandKeyMask | NSShiftKeyMask))) {
        if ([event isLeft]) {
            action = @selector(showPreviousView);
        }
        else if ([event isRight]) {
            action = @selector(showNextView);
        }
    }
    else if ((!isEditing) && ([event modifierKeysFlags] == NSCommandKeyMask)) {
        if ([event isLeft]) {
            action = @selector(navigateBack);
        }
        else if ([event isRight]) {
            action = @selector(showSelectedAccount);
        }
    }
    MGMainWindowController *delegate = [self delegate];
    if ((action != nil) && ([delegate validateAction:action])) {
        [delegate performSelector:action withObject:delegate];
        return YES;
    }
    return [super performKeyEquivalent:event];
}
@end
