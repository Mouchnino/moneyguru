/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGOutlineView.h"

@implementation MGOutlineView
/* NSOutlineView overrides */

- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event])
    {
        [super keyDown:event];
    }
}

- (void)setDelegate:(id)aDelegate
{
    [super setDelegate:aDelegate];
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(outlineViewWasDoubleClicked:)])
    {
        [self setTarget:[self delegate]];
        [self setDoubleAction:@selector(outlineViewWasDoubleClicked:)];
    }
}

- (BOOL)shouldEditTableColumn:(NSTableColumn *)column row:(NSInteger)row
{
    BOOL result = [super shouldEditTableColumn:column row:row];
    if (!result)
        return result;
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(outlineView:shouldEditTableColumn:item:)])
        return [delegate outlineView:self shouldEditTableColumn:column item:[self itemAtRow:row]];
    return YES;
}

/* Notifications & Delegate */

- (void)textDidEndEditing:(NSNotification *)notification
{
    notification = [self processTextDidEndEditing:notification];
    NSView *nextKeyView = [self nextKeyView];
    [self setNextKeyView:nil];
    [super textDidEndEditing:notification];
    [self setNextKeyView:nextKeyView];
    
    if ([self editedColumn] == -1)
    {
        if (!manualEditionStop)
        {
            id delegate = [self delegate];
            if ([delegate respondsToSelector:@selector(outlineViewDidEndEditing:)])
            {
                [delegate outlineViewDidEndEditing:self];
            }
        }
        // We may have lost the focus
        [[self window] makeFirstResponder:self];
    }
}

- (BOOL)textView:(NSTextView *)textView doCommandBySelector:(SEL)command
{
    if (command == @selector(cancelOperation:))
    {
        [self stopEditing]; // The stop editing has to happen before the cancelEdits
        id delegate = [self delegate];
        if ([delegate respondsToSelector:@selector(outlineViewCancelsEdition:)])
        {
            [delegate outlineViewCancelsEdition:self];
        }
        return YES;
    }
    return NO;
}

/* Public */

- (void)selectPath:(NSIndexPath *)aPath
{
    // Make sure the path to aPath is expanded.
    NSIndexPath *path = [NSIndexPath indexPathWithIndex:[aPath indexAtPosition:0]];
    for (int i=1; i<[aPath length]; i++)
    {
        [self expandItem:path];
        path = [path indexPathByAddingIndex:[aPath indexAtPosition:i]];
    }
    NSIndexSet *selected = [NSIndexSet indexSetWithIndex:[self rowForItem:aPath]];
    [self selectRowIndexes:selected byExtendingSelection:NO];
}

- (void)stopEditing
{
    // If we're not editing, don't do anything because we don't want to steal focus from another view
    if ([self editedColumn] >= 0)
    {
        manualEditionStop = YES;
        [[self window] makeFirstResponder:self]; // This will abort edition
        manualEditionStop = NO;
    }
}

- (void)updateSelection
{
    NSIndexPath *selected = [[self delegate] selectedIndexPath];
    [self selectPath:selected];
}

/* BIG HACK ZONE
When tracking clicks in the NSTextField, the NSTableView goes in edition mode even if we click on the
arrow or the button. The only way I found to avoid this is this scheme: let the MGOutlineView know
of the event that caused the click, and don't go in edit mode if it happens.
*/

- (void)ignoreEventForEdition:(NSEvent *)aEvent
{
    eventToIgnore = aEvent;
}

- (void)editColumn:(NSInteger)columnIndex row:(NSInteger)rowIndex withEvent:(NSEvent *)theEvent select:(BOOL)flag
{
    if ((theEvent != nil) && (theEvent == eventToIgnore))
        return;
    [super editColumn:columnIndex row:rowIndex withEvent:theEvent select:flag];
}

@end
