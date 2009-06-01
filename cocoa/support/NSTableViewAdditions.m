#import "NSTableViewAdditions.h"
#import "NSEventAdditions.h"
#import "Utils.h"

@implementation NSTableView(NSTableViewAdditions)

/* Private methods */

// Alright, this is a hack. It has been added to put in common some table and outline code, but the
// thing is an outline view delegate doesn't use tableView:shouldEditTableColumn:row:. Anyway, for 
// the outline, just using [column isEditable] works in moneyGuru for now, so we can keep it that way.
- (BOOL)shouldEditTableColumn:(NSTableColumn *)column row:(int)row
{
    if (![column isEditable])
        return NO;
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(tableView:shouldEditTableColumn:row:)])
    {
        return [delegate tableView:self shouldEditTableColumn:column row:row];
    }
    else
    {
        return YES;
    }
}

/* Public Methods */

// Returns whether the responder chain should be stopeed or not
- (BOOL)dispatchSpecialKeys:(NSEvent *)event
{
    id delegate = [self delegate];
    bool stopChain = NO;
    if ([event isDeleteOrBackspace] && [delegate respondsToSelector:@selector(tableViewHadDeletePressed:)])
	{
        stopChain = [delegate tableViewHadDeletePressed:self];
	}
    if ([event isReturnOrEnter] && [delegate respondsToSelector:@selector(tableViewHadReturnPressed:)])
	{
        stopChain = [delegate tableViewHadReturnPressed:self];
	}
	if ([event isSpace] && [delegate respondsToSelector:@selector(tableViewHadSpacePressed:)])
	{
        stopChain = [delegate tableViewHadSpacePressed:self];
	}
	if ([event isTab]) 
	{
		stopChain = YES;
		[[self window] makeFirstResponder:[self nextValidKeyView]];
	}
	if ([event isBackTab]) 
	{
		stopChain = YES;
		// Ok, this is a big hack. the normal handling of NSTableView must handle this, but we must skip over
		// a NSClipView and a NSScrollView before getting to the actual previousValidKeyView.
		// However, when we are not in Full Keyboard Access mode, there's no problem. Thus, we assume that
		// when previousValidKeyView's class is a NSClipView, it means we must perform the hack
        NSView *previous = [self previousValidKeyView];
        if ([[previous className] isEqualTo:@"NSClipView"]) // Can't use isKindOfClass, we don't want to test for a subclass
            previous = [[previous previousValidKeyView] previousValidKeyView];
        [[self window] makeFirstResponder:previous];
	}
    return stopChain;
}

- (NSNotification *)processTextDidEndEditing:(NSNotification *)notification;
{
    NSDictionary *userInfo = [notification userInfo];
	int textMovement = [[userInfo valueForKey:@"NSTextMovement"] intValue];
	// Do we want to get out of edit mode?
	bool getOutOfEditMode = NO;
    if ([Utils isTiger]) // Tiger doesn't stop editing at the end of the line.
    {
        NSArray *columns = [self tableColumns];
        int row = [self editedRow];
        if (textMovement == NSTabTextMovement)
    	{
    		getOutOfEditMode = YES;
    		for (int i=[self editedColumn]+1; i<[columns count]; i++)
    		{
    			NSTableColumn *column = [columns objectAtIndex:i];
                if ([self shouldEditTableColumn:column row:row]) 
    			{
    				getOutOfEditMode = NO;
    				break;
    			}
    		}
    	}
    	else if (textMovement == NSBacktabTextMovement)
    	{
    		getOutOfEditMode = YES;
    		for (int i=[self editedColumn]-1; i>=0; i--)
    		{
    			NSTableColumn *column = [columns objectAtIndex:i];
    			if ([self shouldEditTableColumn:column row:row])
    			{
    				getOutOfEditMode = NO;
    				break;
    			}
    		}
    	}
    }
	if (textMovement == NSReturnTextMovement)
	{
        getOutOfEditMode = YES;
	}
	if (getOutOfEditMode)
	{
		NSMutableDictionary *newInfo;
        newInfo = [NSMutableDictionary dictionaryWithDictionary:userInfo];
        [newInfo setObject:[NSNumber numberWithInt:NSIllegalTextMovement] forKey:@"NSTextMovement"];
        notification = [NSNotification notificationWithName:[notification name] object:[notification object] userInfo:newInfo];
	}
    return notification;
}

- (void)startEditing
{
    // Make sure one row is selected
    if ([self selectedRow] == -1)
    {
        return;
    }
    
    // We only want to edit columns that are editable. If there aren't any, don't edit.
    for (int i=0;i<[[self tableColumns] count];i++)
    {
        NSTableColumn *col = [[self tableColumns] objectAtIndex:i];
        if ([self shouldEditTableColumn:col row:[self selectedRow]])
        {
            // We only want one row to be selected.
            NSIndexSet *selection = [NSIndexSet indexSetWithIndex:[self selectedRow]];
            [self selectRowIndexes:selection byExtendingSelection:NO];
        	[self editColumn:i row:[self selectedRow] withEvent:nil select:YES];
            break;
        }
    }
}
@end
