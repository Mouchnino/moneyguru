/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "BSD" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/bsd_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGTableView.h"
#import "MGSplitTable.h"
#import "PySchedulePanel.h"

@interface MGSchedulePanel : MGPanel {
    IBOutlet NSTabView *tabView;
    IBOutlet NSTextField *startDateField;
    IBOutlet NSTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatOptionsPopUp;
    IBOutlet NSTextField *stopDateField;
    IBOutlet NSTextField *descriptionField;
    IBOutlet NSTextField *payeeField;
    IBOutlet NSTextField *checknoField;
    IBOutlet NSTextField *notesField;
    IBOutlet MGTableView *splitTableView;
    
    MGSplitTable *splitTable;
}
- (id)initWithParent:(HSWindowController *)aParent;
- (PySchedulePanel *)py;
/* Actions */
- (IBAction)addSplit:(id)sender;
- (IBAction)deleteSplit:(id)sender;
- (IBAction)repeatTypeSelected:(id)sender;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
- (void)refreshRepeatOptions;
@end
