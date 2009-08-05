/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import "MGUnreconciliationDialog.h"

@implementation MGUnreconciliationDialog
+ (int)shouldUnreconcileWithAffectedSplitCount:(int)affectedSplitCount
{
    MGUnreconciliationDialog *dialog = [[MGUnreconciliationDialog alloc] initWithAffectedSplitCount:affectedSplitCount];
    int result = [NSApp runModalForWindow:[dialog window]];
    [[dialog window] close];
    [dialog release];
    return result;
}

- (id)initWithAffectedSplitCount:(int)affectedSplitCount
{
    self = [super initWithWindowNibName:@"UnreconciliationDialog"];
    [self loadWindow];
    NSString *entries = affectedSplitCount > 1 ? @"entries" : @"entry";
    NSString *msg = [NSString stringWithFormat:@"This action will remove reconciliation for %d %@. Continue?",affectedSplitCount,entries];
    [messageTextField setStringValue:msg];
    return self;
}

- (IBAction)go:(id)sender
{
    int result = MGUnreconciliationDialogAbortAction;
    int selectedIndex = [actionChooser indexOfSelectedItem];
    if (selectedIndex == 1)
        result = MGUnreconciliationDialogContinueActionAndUnreconcile;
    else if (selectedIndex == 2)
        result = MGUnreconciliationDialogContinueActionAndDontUnreconcile;
    [NSApp stopModalWithCode:result];
}
@end