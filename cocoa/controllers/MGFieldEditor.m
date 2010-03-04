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
    Class pyClass = [Utils classNamed:@"PyCompletableEdit"];
    py = [[pyClass alloc] initWithCocoa:self];
    lastCompletion = nil;
    [self setEditable:YES];
    [self setFieldEditor:YES];
    [self setSelectable:YES];
    return self;
}

- (void)dealloc
{
    [lastCompletion release];
    [py release];
    [super dealloc];
}

- (NSString *)selectedText
{
    NSRange sel = [self selectedRange];
    if (sel.length == 0) {
        return nil;
    } 
    NSString *text = [self string];
    return [text substringWithRange:sel];
}

- (void)setSource:(PyGUI *)source
{
    [py setSource:source];
    [lastCompletion release];
    lastCompletion = nil;
}

- (void)setAttrname:(NSString *)attrname
{
    [py setAttrname:attrname];
    [lastCompletion release];
    lastCompletion = nil;
}

- (void)moveUp:(id)sender 
{
    [py up];
}

- (void)moveDown:(id)sender
{
    [py down];
}

- (void)insertText:(NSString *)text
{
    [super insertText:text];
    NSString *newText = [self string];
    NSString *selected = [self selectedText];
    // Remove the completion part
    if ((selected != nil) && ([selected isEqualTo:lastCompletion])) {
        newText = [newText substringToIndex:([newText length] - [selected length])];
    }
    [py setText:newText];
}

- (BOOL)resignFirstResponder
{
    /* We only want to commit completion if we actually have one. The conditions below prevent 2
     * bogus cases:
     * 1. The user deleted the completion
     * 2. No changes have been made to the text view, which was pre-populated and selected
    */
    NSString *selected = [self selectedText];
    if ((selected != nil) && ([selected isEqualTo:lastCompletion])) {
        [py commit];
    }
    return [super resignFirstResponder];
}

/* Python --> Cocoa */
- (void)refresh
{
    NSString *text = [py text];
    NSString *completion = [py completion];
    NSInteger insertionPoint = [text length];
    // don't use insertText here: infinite loop hazard.
    [self setString:[text stringByAppendingString:completion]];
    [self setSelectedRange:NSMakeRange(insertionPoint, [completion length])];
    [self scrollRangeToVisible:NSMakeRange(insertionPoint, 0)];
    [lastCompletion release];
    lastCompletion = [completion retain];
}
@end
