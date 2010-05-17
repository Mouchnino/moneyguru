/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGMainWindow.h"
#import "NSEventAdditions.h"

@implementation MGMainWindow
- (BOOL)performKeyEquivalent:(NSEvent *)event 
{
    SEL action = nil;
    if ([event modifierKeysFlags] == (NSCommandKeyMask | NSShiftKeyMask)) {
        if ([event isLeft]) {
            action = @selector(showPreviousView:);
        }
        else if ([event isRight]) {
            action = @selector(showNextView:);
        }
    }
    else if ([event modifierKeysFlags] == NSCommandKeyMask) {
        if ([event isLeft]) {
            action = @selector(navigateBack:);
        }
        else if ([event isRight]) {
            action = @selector(showSelectedAccount:);
        }
    }
    id delegate = [self delegate];
    if ((action != nil) && ([delegate validateAction:action])) {
        [delegate performSelector:action withObject:delegate];
        return YES;
    }
    return NO;
}
@end
