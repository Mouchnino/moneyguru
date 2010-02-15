/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGFieldEditor.h"
#import "Utils.h"

@implementation MGFieldEditor
- (id)init
{
    self = [super initWithFrame:NSMakeRect(0, 0, 0, 0)];
    [self setEditable:YES];
    [self setFieldEditor:YES];
    [self setSelectable:YES];
    return self;
}

- (void)moveUp:(id)sender 
{
    id delegate = [self delegate];
    if (delegate && [delegate respondsToSelector:@selector(fieldEditorWantsPrevValue:)]) {
        [self replaceWith:[delegate fieldEditorWantsPrevValue:self]];
    }
}

- (void)moveDown:(id)sender
{
    id delegate = [self delegate];
    if (delegate && [delegate respondsToSelector:@selector(fieldEditorWantsNextValue:)]) {
        [self replaceWith:[delegate fieldEditorWantsNextValue:self]];
    }
}

- (void)insertText:(NSString *)text
{
    [super insertText:text];
    id delegate = [self delegate];
    if ((delegate) && ([delegate respondsToSelector:@selector(fieldEditor:wantsCompletionFor:)]) &&
        [self selectedRange].location == [[self string] length])  // only complete if we are at the end of the input
    {
        [self completeWith:[delegate fieldEditor:self wantsCompletionFor:[self string]]];
    }
}

- (BOOL)resignFirstResponder
{
    id delegate = [self delegate];
    // We complete only if we are actually displaying a proposition.
    // If the user typed out the proposition completely with a different case, it's an explicit
    // statement that he doesn't want any replacement to occur. If the selection starts on the
    // first character, the user didn't type anything in the field and no completion has been
    // suggested yet.
    if ([self selectedRange].length > 0 && [self selectedRange].location > 0 &&
        delegate && [delegate respondsToSelector:@selector(fieldEditorWantsCurrentValue:)])
    {
        NSString *completion = [[self delegate] fieldEditorWantsCurrentValue:self];
        if (completion != nil) {
            [self setString:completion];
        }
    }
    return [super resignFirstResponder];
}

/* Methods */

- (void)completeWith:(NSString *)proposition
{
    if (proposition == nil)
    {
        return;
    }
    NSString *current = [self string];
    NSInteger insertionPoint = [current length];
    NSString *suffix = [proposition substringFromIndex:[current length]];
    [self setString:[current stringByAppendingString:suffix]];    // don't use insertText here: infinite loop hazard.
    [self setSelectedRange:NSMakeRange(insertionPoint, [suffix length])];
    [self scrollRangeToVisible:NSMakeRange(insertionPoint, 0)];
}

- (void)replaceWith:(NSString *)text
{
    if (text == nil)
    {
        return;
    }
    NSRange selection = [self selectedRange];
    NSInteger selectionStart = selection.length == 0 ? 0 : selection.location;
    NSString *oldPrefix = [[[self string] substringToIndex:selectionStart] lowercaseString];
    NSString *newPrefix = [[text substringToIndex:selectionStart] lowercaseString];
    if (![oldPrefix isEqualToString:newPrefix])
    {
        selectionStart = 0;
    }
    [self setString:text];
    [self setSelectedRange:NSMakeRange(selectionStart, [text length] - selectionStart)];
    [self scrollRangeToVisible:NSMakeRange(selectionStart, 0)];
}
@end
