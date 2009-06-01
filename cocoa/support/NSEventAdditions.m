#import "NSEventAdditions.h"

@implementation NSEvent(NSEventAdditions)

- (unichar)firstCharacter
{
    NSString *characters = [self characters];
    if ([characters length] == 0)
    {
        return nil;
    }
    return [characters characterAtIndex:0];
}

- (unsigned int)flags
{
    // get flags and strip the lower 16 (device dependant) bits
    // See modifierFlags's doc for details
    return [self modifierFlags] & 0x00ff;
}

- (BOOL)isDeleteOrBackspace
{
    unichar firstChar = [self firstCharacter];
    return firstChar == NSDeleteFunctionKey || firstChar == NSDeleteCharFunctionKey || 
           firstChar == NSDeleteCharacter || firstChar == NSBackspaceCharacter;
}

- (BOOL)isReturnOrEnter
{
    unichar firstChar = [self firstCharacter];
    return firstChar == NSCarriageReturnCharacter || firstChar == NSEnterCharacter;
}

- (BOOL)isTab
{
    return [self firstCharacter] == NSTabCharacter;
}

- (BOOL)isBackTab
{
    return [self firstCharacter] == NSBackTabCharacter;
}

- (BOOL)isUp
{
    return [self firstCharacter] == NSUpArrowFunctionKey;
}

- (BOOL)isDown
{
    return [self firstCharacter] == NSDownArrowFunctionKey;
}

- (BOOL)isSpace
{
    return ([self firstCharacter] == 0x20) && (![self flags]);
}

@end
