/* 
Copyright 2010 Hardcoded Software (http://www.hardcoded.net)

This software is licensed under the "HS" License as described in the "LICENSE" file, 
which should be included with this package. The terms are also available at 
http://www.hardcoded.net/licenses/hs_license
*/

#import <Cocoa/Cocoa.h>
#import "MGPanel.h"
#import "MGDocument.h"
#import "MGTextField.h"
#import "MGTableView.h"
#import "MGSplitTable.h"
#import "PySchedulePanel.h"

@interface MGSchedulePanel : MGPanel {
    IBOutlet NSTabView *tabView;
    IBOutlet MGTextField *startDateField;
    IBOutlet MGTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatOptionsPopUp;
    IBOutlet MGTextField *stopDateField;
    IBOutlet MGTextField *descriptionField;
    IBOutlet MGTextField *payeeField;
    IBOutlet NSTextField *checknoField;
    IBOutlet NSTextField *notesField;
    IBOutlet NSTextField *amountField;
    IBOutlet NSTextField *amountField2;
    IBOutlet NSTextField *mctNotice;
    IBOutlet NSTextField *mctNotice2;
    IBOutlet MGTableView *splitTableView;
    
    MGSplitTable *splitTable;
    NSTextView *customFieldEditor;
    NSTextView *customDateFieldEditor;
}
- (PySchedulePanel *)py;
/* Actions */
- (IBAction)addSplit:(id)sender;
- (IBAction)deleteSplit:(id)sender;
- (IBAction)repeatTypeSelected:(id)sender;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
- (void)refreshRepeatOptions;
@end
