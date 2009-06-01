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