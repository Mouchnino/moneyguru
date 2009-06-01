#import <Cocoa/Cocoa.h>

@interface NSEvent(NSEventAdditions)
- (unichar)firstCharacter;
- (unsigned int)flags;
- (BOOL)isDeleteOrBackspace;
- (BOOL)isReturnOrEnter;
- (BOOL)isTab;
- (BOOL)isBackTab;
- (BOOL)isUp;
- (BOOL)isDown;
- (BOOL)isSpace;
@end
