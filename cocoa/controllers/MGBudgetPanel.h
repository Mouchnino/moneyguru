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
#import "PyBudgetPanel.h"

@interface MGBudgetPanel : MGPanel {
    IBOutlet MGTextField *startDateField;
    IBOutlet MGTextField *repeatEveryField;
    IBOutlet NSTextField *repeatEveryDescLabel;
    IBOutlet NSPopUpButton *repeatOptionsPopUp;
    IBOutlet MGTextField *stopDateField;
    IBOutlet NSPopUpButton *accountSelector;
    IBOutlet NSPopUpButton *targetSelector;
    IBOutlet MGTextField *amountField;
    IBOutlet NSTextField *notesField;
    
    NSTextView *customDateFieldEditor;
}
- (PyBudgetPanel *)py;
/* Actions */
- (IBAction)repeatTypeSelected:(id)sender;
/* Python --> Cocoa */
- (void)refreshRepeatEvery;
- (void)refreshRepeatOptions;
@end
