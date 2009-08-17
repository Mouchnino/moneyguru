/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGTableView.h"
#import "MGFieldEditor.h"
#import "NSEventAdditions.h"

@implementation MGTableView
- (void)awakeFromNib
{
    /* Respond to double-clicks */
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(tableViewWasDoubleClicked:)])
    {
        [self setTarget:[self delegate]];
        [self setDoubleAction:@selector(tableViewWasDoubleClicked:)];
    }
}

/* NSTableView */

- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event])
	{
        [super keyDown:event];
	}
}

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
	        if ([delegate respondsToSelector:@selector(tableViewDidEndEditing:)])
	        {
		        [delegate tableViewDidEndEditing:self];
	        }
	    }
        // We may have lost the focus
        [[self window] makeFirstResponder:self];
	}
}

/* NSTextView delegate */

- (BOOL)textView:(NSTextView *)textView doCommandBySelector:(SEL)command
{
    if (command == @selector(cancelOperation:))
    {
        [self stopEditing]; // The stop editing has to happen before the cancelEdits
        id delegate = [self delegate];
        if ([delegate respondsToSelector:@selector(tableViewCancelsEdition:)])
        {
	        [delegate tableViewCancelsEdition:self];
        }
        return YES;
    }
	return NO;
}

/* MGFieldEditor delegate */

- (NSString *)fieldEditor:(MGFieldEditor *)fieldEditor wantsCompletionFor:(NSString *)text
{
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(autoCompletionForColumn:partialWord:)])
    {
        NSTableColumn *editedColumn = [[self tableColumns] objectAtIndex:[self editedColumn]];
        return [delegate autoCompletionForColumn:editedColumn partialWord:text];
    }
	return nil;
}

- (NSString *)fieldEditorWantsCurrentValue:(MGFieldEditor *)fieldEditor
{
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(currentValueForColumn:)])
    {
        NSTableColumn *editedColumn = [[self tableColumns] objectAtIndex:[self editedColumn]];
        return [delegate currentValueForColumn:editedColumn];
    }
    return nil;
}

- (NSString *)fieldEditorWantsPrevValue:(MGFieldEditor *)fieldEditor
{
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(prevValueForColumn:)])
    {
        NSTableColumn *editedColumn = [[self tableColumns] objectAtIndex:[self editedColumn]];
        return [delegate prevValueForColumn:editedColumn];
    }
    return nil;
}

- (NSString *)fieldEditorWantsNextValue:(MGFieldEditor *)fieldEditor
{
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(nextValueForColumn:)])
    {
        NSTableColumn *editedColumn = [[self tableColumns] objectAtIndex:[self editedColumn]];
        return [delegate nextValueForColumn:editedColumn];
    }
    return nil;
}

/* Public methods */

- (void)updateSelection
{
    NSIndexSet *selection = [[self delegate] selectedIndexes];
	[self selectRowIndexes:selection byExtendingSelection:NO];
}

// Calling this does not result in a tableViewDidEndEditing: call
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

@end
