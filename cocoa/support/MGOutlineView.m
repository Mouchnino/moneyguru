#import "MGOutlineView.h"

@implementation MGOutlineView

- (void)awakeFromNib
{
    /* Respond to double-clicks */
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(outlineViewWasDoubleClicked:)])
    {
        [self setTarget:[self delegate]];
        [self setDoubleAction:@selector(outlineViewWasDoubleClicked:)];
    }
}

/* NSResponder */

- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event])
    {
        [super keyDown:event];
    }
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

- (void)editColumn:(int)columnIndex row:(int)rowIndex withEvent:(NSEvent *)theEvent select:(BOOL)flag
{
    if ((theEvent != nil) && (theEvent == eventToIgnore))
        return;
    [super editColumn:columnIndex row:rowIndex withEvent:theEvent select:flag];
}

@end
