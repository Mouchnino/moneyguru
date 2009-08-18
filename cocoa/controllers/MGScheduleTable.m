/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGScheduleTable.h"
#import "Utils.h"
#import "MGConst.h"
#import "MGFieldEditor.h"

@implementation MGScheduleTable

- (id)initWithDocument:(MGDocument *)aDocument
{
    self = [super initWithPyClassName:@"PyScheduleTable" pyParent:[aDocument py]];
    [NSBundle loadNibNamed:@"ScheduleTable" owner:self];
    schedulePanel = [[MGSchedulePanel alloc] initWithDocument:aDocument];
    return self;
}

- (void)dealloc
{
    [schedulePanel release];
    [super dealloc];
}
        
/* Overrides */
- (PyScheduleTable *)py
{
    return (PyScheduleTable *)py;
}

/* Public */
- (void)add
{
    [schedulePanel new];
    [NSApp beginSheet:[schedulePanel window] modalForWindow:[[self view] window] modalDelegate:self 
        didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
}

- (void)deleteSelected
{
    [[self py] deleteSelectedRows];
}

- (void)editSelected
{
    if ([schedulePanel canLoad])
    {
        [schedulePanel load];
        [NSApp beginSheet:[schedulePanel window] modalForWindow:[[self view] window] modalDelegate:self 
            didEndSelector:@selector(didEndSheet:returnCode:contextInfo:) contextInfo:nil];
    }
}

/* Delegate */
// MGTableView
- (BOOL)tableViewHadReturnPressed:(NSTableView *)tableView
{
    [self editSelected];
    return YES;
}

- (void)tableViewWasDoubleClicked:(MGTableView *)tableView
{
    [self editSelected];
}

// sheet
- (void)didEndSheet:(NSWindow *)sheet returnCode:(int)returnCode contextInfo:(void *)contextInfo
{
    [sheet orderOut:nil];
}

@end