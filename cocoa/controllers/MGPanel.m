/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import "MGPanel.h"

@implementation MGPanel
- (id)initWithNibName:(NSString *)aNibName pyClassName:(NSString *)aClassName parent:(HSWindowController *)aParent
{
    self = [super initWithNibName:aNibName pyClassName:aClassName pyParent:[aParent py]];
    [self window]; // Initialize elements from the NIB.
    parentWindow = [aParent window];
    customFieldEditor = [[MGFieldEditor alloc] initWithPyParent:[aParent py]];
    customDateFieldEditor = [[MGDateFieldEditor alloc] init];
    return self;
}

- (void)dealloc
{
    [customDateFieldEditor release];
    [customFieldEditor release];
    [super dealloc];
}

- (PyPanel *)py
{
    return (PyPanel *)py;
}

/* Virtual */
- (NSString *)completionAttrForField:(id)aField
{
    // if textField is a field to perform auto-complete on, return the name of the field for auto-completion
    return nil;
}

- (BOOL)isFieldDateField:(id)aField
{
    return NO;
}

- (NSResponder *)firstField
{
    // The first field to get focus after a load
    return nil;
}

- (void)loadFields
{
}

- (void)saveFields
{
}

/* Public */
- (void)save
{
    [[self py] savePanel];
}

/* Actions */
- (IBAction)cancel:(id)sender
{
    [NSApp endSheet:[self window]];
}

- (IBAction)save:(id)sender
{
    [self save];
    [NSApp endSheet:[self window]];
}

/* Delegate */
- (id)windowWillReturnFieldEditor:(NSWindow *)window toObject:(id)asker
{
    if ([self isFieldDateField:asker]) {
        return customDateFieldEditor;
    }
    else {
        NSString *attrname = [self completionAttrForField:asker];
        if (attrname != nil) {
            [customFieldEditor setAttrname:attrname];
            return customFieldEditor;
        }
    }
    return nil;
}

- (void)didEndSheet:(NSWindow *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo
{
    [sheet orderOut:nil];
}

/* Python --> Cocoa */
- (void)preLoad
{
    // If the date field is already the first responder, the date being set will not correctly go down
    // the py widget during makeFirstResponder:
    [[self window] makeFirstResponder:nil];
}

- (void)postLoad
{
    // When we change the values in the py side, it doesn't work with KVO mechanism.
    // Notifications of a "py" change is enough to refresh all bound controls.
    [self willChangeValueForKey:@"py"];
    [self didChangeValueForKey:@"py"];
    [self loadFields];
    [[self window] makeFirstResponder:[self firstField]];
    [NSApp beginSheet:[self window] modalForWindow:parentWindow modalDelegate:self 
            didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (void)preSave
{
    // Sometimes, the last edited fields doesn't have the time to flush its data before savePanel
    // is called (Not when you press Return to Save, but when you click on Save, it happens).
    // This is what the line below is for.
    [[self window] makeFirstResponder:[self window]];
    [self saveFields];
}
@end