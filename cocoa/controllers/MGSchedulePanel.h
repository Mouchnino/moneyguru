/* 
Copyright 2011 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGTableView.h"
#import "MGSplitTable.h"
#import "HSPopUpList.h"
#import "PySchedulePanel.h"

@class MGMainWindowController;

@interface MGSchedulePanel : MGPanel {
    IBOutlet NSTabView *tabView;
    IBOutlet NSTextField *startDateField;
    IBOutlet NSTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatTypePopUpView;
    IBOutlet NSTextField *stopDateField;
    IBOutlet NSTextField *descriptionField;
    IBOutlet NSTextField *payeeField;
    IBOutlet NSTextField *checknoField;
    IBOutlet NSTextField *notesField;
    IBOutlet MGTableView *splitTableView;
    
    MGSplitTable *splitTable;
    HSPopUpList *repeatTypePopUp;
}
- (id)initWithParent:(MGMainWindowController *)aParent;
- (PySchedulePanel *)model;
/* Actions */
- (IBAction)addSplit:(id)sender;
- (IBAction)deleteSplit:(id)sender;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
@end
