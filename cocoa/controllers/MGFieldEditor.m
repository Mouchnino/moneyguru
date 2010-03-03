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
    if ([[py text] length]) {
        [py up];
        [self refresh];
    }
}

- (void)moveDown:(id)sender
{
    if ([[py text] length]) {
        [py down];
        [self refresh];
    }
}

- (void)insertText:(NSString *)text
{
    [super insertText:text];
    NSString *newText = [self string];
    // Remove the completion part
    if ((lastCompletion != nil) && ([newText hasSuffix:lastCompletion])) {
        newText = [newText substringToIndex:([newText length] - [lastCompletion length])];
    }
    [py setText:newText];
    [self refresh];
}

- (BOOL)resignFirstResponder
{
    /* We only want to commit completion if we actually have one. The conditions below prevent 2
     * bogus cases:
     * 1. The user deleted the completion
     * 2. No changes have been made to the text view, which was pre-populated and selected
    */
    if (([self selectedRange].length > 0) && (lastCompletion != nil)) {
        [py commit];
        [self refresh];
    }
    return [super resignFirstResponder];
}
@end
