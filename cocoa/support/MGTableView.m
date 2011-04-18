/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGTableView.h"
#import "NSEventAdditions.h"

@implementation MGTableView
/* NSTableView */
- (void)keyDown:(NSEvent *)event 
{
    if (![self dispatchSpecialKeys:event]) {
        [super keyDown:event];
	}
}

- (void)setDelegate:(id)aDelegate
{
    [super setDelegate:aDelegate];
    id delegate = [self delegate];
    if ([delegate respondsToSelector:@selector(tableViewWasDoubleClicked:)]) {
        [self setTarget:[self delegate]];
        [self setDoubleAction:@selector(tableViewWasDoubleClicked:)];
    }
}

- (void)textDidEndEditing:(NSNotification *)notification
{
    notification = [self processTextDidEndEditing:notification];
    NSView *nextKeyView = [self nextKeyView];
    [self setNextKeyView:nil];
    [super textDidEndEditing:notification];
    [self setNextKeyView:nextKeyView];
    
	if ([self editedColumn] == -1) {
	    if (!manualEditionStop) {
	        id delegate = [self delegate];
	        if ([delegate respondsToSelector:@selector(tableViewDidEndEditing:)]) {
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
    if (command == @selector(cancelOperation:)) {
        [self stopEditing]; // The stop editing has to happen before the cancelEdits
        id delegate = [self delegate];
        if ([delegate respondsToSelector:@selector(tableViewCancelsEdition:)]) {
	        [delegate tableViewCancelsEdition:self];
        }
        return YES;
    }
	return NO;
}

/* Actions */
- (IBAction)copy:(id)sender
{
    NSString *data = [[self delegate] dataForCopyToPasteboard];
    NSPasteboard *p = [NSPasteboard generalPasteboard];
    [p declareTypes:[NSArray arrayWithObjects:NSStringPboardType, nil] owner:nil];
    [p setString:data forType:NSStringPboardType];
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
    if ([self editedColumn] >= 0) {
        manualEditionStop = YES;
        [[self window] makeFirstResponder:self]; // This will abort edition
        manualEditionStop = NO;
    }
}

@end
