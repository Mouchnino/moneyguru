#import <Cocoa/Cocoa.h>

#define MGUnreconciliationDialogAbortAction 0
#define MGUnreconciliationDialogContinueActionAndUnreconcile 1
#define MGUnreconciliationDialogContinueActionAndDontUnreconcile 2

@interface MGUnreconciliationDialog : NSWindowController
{
    IBOutlet NSPopUpButton *actionChooser;
    IBOutlet NSTextField *messageTextField;
}
+ (int)shouldUnreconcileWithAffectedSplitCount:(int)affectedSplitCount;

- (id)initWithAffectedSplitCount:(int)affectedSplitCount;

- (IBAction)go:(id)sender;
@end