/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGGUIController.h"

@implementation MGGUIController
// Python --> Cocoa
- (void)showMessage:(NSString *)msg
{
    NSAlert *a = [NSAlert alertWithMessageText:msg defaultButton:nil alternateButton:nil 
        otherButton:nil informativeTextWithFormat:@""];
    [a beginSheetModalForWindow:[[self view] window] modalDelegate:self didEndSelector:nil 
        contextInfo:nil];
}

@end
