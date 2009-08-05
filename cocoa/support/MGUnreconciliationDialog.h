/* 
Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

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