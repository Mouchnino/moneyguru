/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGFieldEditor.h"
#import "Utils.h"
#import "MGUtils.h"

@implementation MGFieldEditor
- (id)init
{
    self = [super initWithFrame:NSMakeRect(0, 0, 0, 0)];
    Class PyDateWidget = [MGUtils classNamed:@"PyDateWidget"];
    pyDate = [[PyDateWidget alloc] init];
    [self setEditable:YES];
    [self setFieldEditor:YES];
    [self setSelectable:YES];
    dateMode = NO;
    return self;
}

- (void)dealloc
{
    [pyDate release];
    [super dealloc];
}

- (void)moveUp:(id)sender 
{
    if (dateMode)
    {
        [pyDate increase];
        [self dateRefresh];
    }
    else
    {
        id delegate = [self delegate];
        if (delegate && [delegate respondsToSelector:@selector(fieldEditorWantsPrevValue:)])
        {
            [self replaceWith:[delegate fieldEditorWantsPrevValue:self]];
        }
    }
}

- (void)moveDown:(id)sender
{
    if (dateMode)
    {
        [pyDate decrease];
        [self dateRefresh];
    }
    else
    {
        id delegate = [self delegate];
        if (delegate && [delegate respondsToSelector:@selector(fieldEditorWantsNextValue:)])
        {
            [self replaceWith:[delegate fieldEditorWantsNextValue:self]];
        }
    }
}

- (void)insertText:(NSString *)text
{
    if (dateMode)
    {
        [pyDate type:text];
        [self dateRefresh];
    }
    else
    {
        [super insertText:text];
        id delegate = [self delegate];
        if ((delegate) && ([delegate respondsToSelector:@selector(fieldEditor:wantsCompletionFor:)]) &&
            [self selectedRange].location == [[self string] length]  // only complete if we are at the end of the input
            )
        {
            [self completeWith:[delegate fieldEditor:self wantsCompletionFor:[self string]]];
        }
    }
}

- (BOOL)resignFirstResponder
{
    if (dateMode)
    {
        [pyDate exit];
        [self dateRefresh];
    }
    else
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
            if (completion != nil)
            {
                [self setString:completion];
            }
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
    int insertionPoint = [current length];
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
    int selectionStart = selection.length == 0 ? 0 : selection.location;
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

/* DATE STUFF */

- (BOOL)dateMode
{
    return dateMode;
}
- (void)setDateMode:(BOOL)aDateMode
{
    if (aDateMode == dateMode)
        return;
    dateMode = aDateMode;
    if (dateMode)
        [self dateRefresh];
}

- (void)dateRefresh
{
    NSString *old = [self string];
    NSString *new = [pyDate text];
    BOOL changed = ([old length] > 0) && (![old isEqualTo:new]);
    // We *have* to call shouldChangeTextInRange: for the system to work. if we don't, the editor
    // will not set its state as "changed"
    if ((changed) && (![self shouldChangeTextInRange:NSMakeRange(0, [old length]) replacementString:new]))
    {
        // The delegate doesn't want us to do the change
        return;
    }
    [self setString:new];
    NSArray *sel = [pyDate selection];
    int start = n2i([sel objectAtIndex:0]);
    int end = n2i([sel objectAtIndex:1]);
    [self setSelectedRange:NSMakeRange(start, end - start + 1)];
    if (changed)
    {
        [self didChangeText];
    }
}

- (void)deleteForward:(id)sender
{
    if (dateMode)
    {
        [pyDate backspace];
        [self dateRefresh];
    }
    else
        [super deleteForward:sender];
}

- (void)deleteBackward:(id)sender
{
    if (dateMode)
    {
        [pyDate backspace];
        [self dateRefresh];
    }
    else
        [super deleteBackward:sender];
}

- (void)moveLeft:(id)sender 
{
    if (dateMode)
    {
        [pyDate left];
        [self dateRefresh];
    }
    else
        [super moveLeft:sender];
}

- (void)moveRight:(id)sender
{
    if (dateMode)
    {
        [pyDate right];
        [self dateRefresh];
    }
    else
        [super moveRight:sender];
}

- (BOOL)becomeFirstResponder
{
    BOOL result = [super becomeFirstResponder];
    if (dateMode)
    {
        [pyDate setDate:[self string]]; // set the initial date
        // This is rather hacking, but I couldn't find any other alternative. If tabbed in, all the 
        // text is selected, if clicked in, nothing is selected, and this all happense somewhere
        // *after* becomeFirstResponder
        [self performSelector:@selector(dateRefresh) withObject:self afterDelay:0];
    }
    return result;
}

@end
